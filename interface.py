"""Interface do laboratório de PDI — Tkinter, sem dependências de GUI extras."""
from __future__ import annotations
import threading
import queue
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import numpy as np
from PIL import Image, ImageTk

from intensity import negativo, alargamento_constraste, limiarizacao, gamma, logaritmico
from histogram import histograma_expansao, histograma_equalizacao
from filter import filtro_media, filtro_mediana
from contraste import contraste_adaptativo
from edge_detection import roberts, sobel, kirsch, laplaciano
from agucamento import agucamento_laplaciano, high_boost
from convolucao import convolucao

ROOT = Path(__file__).resolve().parent
_BG = '#111827'
_PANEL = '#1e293b'
_TEXT = '#f1f5f9'
_MUTED = '#a7b7cc'
_BLUE = '#38bdf8'


def grayscale(path):
    with Image.open(path) as image:
        return np.asarray(image.convert('L'), dtype=np.uint8).copy()


def uint8(value):
    return np.clip(np.rint(value), 0, 255).astype(np.uint8)


def visual(value, signed=False):
    a = np.asarray(value, dtype=np.float64)
    if signed:
        m = float(np.max(np.abs(a)))
        return uint8(128 + 127 * a / m) if m else np.full(a.shape, 128, np.uint8)
    a = np.abs(a)
    m = float(np.max(a))
    return uint8(255 * a / m) if m else np.zeros(a.shape, np.uint8)


def alternate_image(a, b):
    if b is None:
        raise ValueError('Selecione a segunda imagem para realizar o dissolve.')
    if b.shape != a.shape:
        b_img = Image.fromarray(b).resize((a.shape[1], a.shape[0]), Image.Resampling.BILINEAR)
        b = np.asarray(b_img)
    return b


def apply_operation(name, a, b, args, mask):
    if name == 'Negativo':
        return [('Negativo', np.asarray(negativo(a)))]
    if name == 'Alargamento de contraste':
        return [('Contraste', np.asarray(alargamento_constraste(a)))]
    if name == 'Limiarização':
        return [('Limiarização', np.asarray(limiarizacao(a, int(args['limiar']))))]
    if name == 'Gamma':
        return [('Gamma', np.asarray(gamma(a, float(args['gamma']))))]
    if name == 'Logarítmico':
        return [('Logarítmico', np.asarray(logaritmico(a)))]
    if name == 'Expansão de histograma':
        return [('Expansão', np.asarray(histograma_expansao(a)))]
    if name == 'Equalização de histograma':
        return [('Equalização', np.asarray(histograma_equalizacao(a)))]
    if name.startswith('Dissolve'):
        b = alternate_image(a, b).astype(np.float64)
        a_float = a.astype(np.float64)
        if name == 'Dissolve uniforme':
            alpha = float(args['alpha'])
        else:
            width = a.shape[1]
            alpha = np.linspace(0, 1, width)[None, :]
        return [(name, uint8((1-alpha)*a_float + alpha*b))]
    if name == 'Contraste adaptativo':
        return [('Contraste adaptativo', contraste_adaptativo(a, float(args['c']), int(args['n'])))]
    if name == 'Filtro da média':
        return [('Filtro da média', filtro_media(a, int(args['n'])))]
    if name == 'Filtro da mediana':
        return [('Filtro da mediana', filtro_mediana(a, int(args['n'])))]
    if name in ('Roberts', 'Sobel'):
        data = roberts(a) if name == 'Roberts' else sobel(a)
        return [(f'{name} · magnitude', visual(data['magnitude'])),
                ('Gx (módulo)', visual(data['Gx'])),
                ('Gy (módulo)', visual(data['Gy'])),
                ('Gx (com sinal)', visual(data['Gx'], True)),
                ('Gy (com sinal)', visual(data['Gy'], True))]
    if name == 'Kirsch':
        data = kirsch(a)
        return [('Kirsch · bordas finais', visual(data['bordas']))] + [
            (f'Kirsch · {direction}', visual(v)) for direction, v in data['direcoes'].items()]
    if name == 'Laplaciano':
        data = laplaciano(a)
        return [('Laplaciano · bordas', visual(data['bordas'])),
                ('Laplaciano · resposta com sinal', visual(data['resposta'], True))]
    if name == 'Aguçamento Laplaciano':
        data = agucamento_laplaciano(a, float(args['c']))
        return [('Imagem aguçada', uint8(data['agucada'])),
                ('Resposta Laplaciana (com sinal)', visual(data['laplaciano'], True))]
    if name == 'High Boost':
        data = high_boost(a, float(args['k']), int(args['n']))
        return [('Imagem aguçada', uint8(data['agucada'])),
                ('Imagem suavizada', uint8(data['suavizada'])),
                ('Detalhes (com sinal)', visual(data['detalhes'], True))]
    if name == 'Convolução genérica':
        rows = [line.strip() for line in mask.splitlines() if line.strip()]
        if not rows:
            raise ValueError('Informe uma máscara, com uma linha por linha de coeficientes.')
        values = [[float(x.replace(',', '.')) for x in row.replace(';', ' ').split()] for row in rows]
        if not all(len(row) == len(values[0]) for row in values):
            raise ValueError('Todas as linhas da máscara devem possuir a mesma largura.')
        response = convolucao(a, np.asarray(values), float(args['offset']), args['borda'])
        return [('Convolução · resultado', uint8(response)),
                ('Resposta normalizada (módulo)', visual(response)),
                ('Resposta com sinal', visual(response, True))]
    raise ValueError(f'Operação não reconhecida: {name}')


OPERATIONS = {
    'Algébricas': ['Dissolve uniforme', 'Dissolve não uniforme'],
    'Intensidade': ['Negativo', 'Alargamento de contraste', 'Limiarização', 'Gamma', 'Logarítmico'],
    'Histogramas': ['Expansão de histograma', 'Equalização de histograma'],
    'Contraste e filtros': ['Contraste adaptativo', 'Filtro da média', 'Filtro da mediana'],
    'Detecção de bordas': ['Roberts', 'Sobel', 'Kirsch', 'Laplaciano'],
    'Aguçamento': ['Aguçamento Laplaciano', 'High Boost'],
    'Convolução': ['Convolução genérica'],
}


class Laboratory(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Laboratório PDI')
        self.geometry('1250x790')
        self.minsize(1030, 650)
        self.configure(bg=_BG)
        self.original = None
        self.second = None
        self.path = None
        self.results = []
        self.photo_refs = []
        self.pending = queue.Queue()
        self.is_busy = False
        self.vars = {key: tk.StringVar(value=val) for key, val in {
            'alpha': '0.5', 'n': '3', 'limiar': '128', 'gamma': '0.7',
            'c': '10', 'k': '1.5', 'offset': '0', 'borda': 'reflect'
        }.items()}
        self.operation = tk.StringVar(value='Negativo')
        self._style()
        self._layout()
        self._configure_parameters()
        self.after(120, self._poll)

    def _style(self):
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('PDI.TCombobox', padding=7, fieldbackground='#f8fafc', background='#e2e8f0')
        style.configure('PDI.TScrollbar', background='#64748b')

    def _label(self, parent, text, size=11, color=_TEXT, bold=False, **kwargs):
        return tk.Label(parent, text=text, font=('DejaVu Sans', size, 'bold' if bold else 'normal'),
                        fg=color, bg=parent.cget('bg'), **kwargs)

    def _button(self, parent, text, command, primary=False):
        color = '#0284c7' if primary else '#334155'
        btn = tk.Button(parent, text=text, command=command, bg=color, fg='white',
                        activebackground='#0369a1' if primary else '#475569', activeforeground='white',
                        font=('DejaVu Sans', 10, 'bold'), relief='flat', padx=12, pady=10, cursor='hand2')
        return btn

    def _layout(self):
        header = tk.Frame(self, bg=_BG, padx=24, pady=17)
        header.pack(fill='x')
        self._label(header, 'LABORATÓRIO PDI', 18, bold=True).pack(side='left')
        self._label(header, 'Processamento de imagens 8 bits', 10, color=_MUTED).pack(side='right')
        main = tk.Frame(self, bg=_BG, padx=17, pady=4)
        main.pack(fill='both', expand=True)
   
        sidebar_outer = tk.Frame(main, bg=_PANEL, width=320)
        sidebar_outer.pack(side='left', fill='y', padx=(0, 14))
        sidebar_outer.pack_propagate(False)

        self.sidebar_canvas = tk.Canvas(
            sidebar_outer, bg=_PANEL, highlightthickness=0, bd=0
        )
        sidebar_scroll = ttk.Scrollbar(
            sidebar_outer, orient='vertical', command=self.sidebar_canvas.yview
        )
        self.sidebar_canvas.configure(yscrollcommand=sidebar_scroll.set)
        sidebar_scroll.pack(side='right', fill='y')
        self.sidebar_canvas.pack(side='left', fill='both', expand=True)

        sidebar = tk.Frame(self.sidebar_canvas, bg=_PANEL, padx=17, pady=17)
        self.sidebar_window = self.sidebar_canvas.create_window(
            (0, 0), window=sidebar, anchor='nw'
        )
        sidebar.bind('<Configure>', self._update_sidebar_scrollregion)
        self.sidebar_canvas.bind('<Configure>', self._fit_sidebar_width)
        self.bind_all('<MouseWheel>', self._scroll_sidebar)
        self.bind_all('<Button-4>', self._scroll_sidebar)
        self.bind_all('<Button-5>', self._scroll_sidebar)
        self._label(sidebar, '1  IMAGENS', 10, _BLUE, True).pack(anchor='w', pady=(0, 11))
        self._button(sidebar, 'Abrir imagem principal', self.open_primary, True).pack(fill='x', pady=(0, 7))
        self._button(sidebar, 'Abrir segunda imagem', self.open_secondary).pack(fill='x')
        self.filename_label = self._label(sidebar, 'Nenhuma imagem selecionada', 9, _MUTED, wraplength=260, justify='left')
        self.filename_label.pack(anchor='w', pady=(10, 18))
        self._label(sidebar, '2  OPERAÇÃO', 10, _BLUE, True).pack(anchor='w', pady=(0, 9))
        self.category = ttk.Combobox(sidebar, state='readonly', values=list(OPERATIONS), style='PDI.TCombobox')
        self.category.set('Intensidade')
        self.category.pack(fill='x', pady=(0, 7))
        self.category.bind('<<ComboboxSelected>>', self._change_category)
        self.choices = ttk.Combobox(sidebar, state='readonly', textvariable=self.operation,
                                    values=OPERATIONS['Intensidade'], style='PDI.TCombobox')
        self.choices.pack(fill='x', pady=(0, 15))
        self.choices.bind('<<ComboboxSelected>>', self._configure_parameters)
        self._label(sidebar, '3  PARÂMETROS', 10, _BLUE, True).pack(anchor='w', pady=(0, 8))
        self.parameters = tk.Frame(sidebar, bg=_PANEL)
        self.parameters.pack(fill='x')
        self.mask_label = self._label(sidebar, 'Máscara (linhas separadas por Enter)', 9, _MUTED)
        self.mask_box = tk.Text(sidebar, height=5, bg='#f8fafc', fg='#0f172a', font=('DejaVu Sans Mono', 10), relief='flat')
        self.mask_box.insert('1.0', '0 -1 0\n-1 5 -1\n0 -1 0')
        self.run_button = self._button(sidebar, '▶   Aplicar operação', self.run_operation, True)
        self.run_button.pack(fill='x', pady=(18, 7))
        self._button(sidebar, 'Restaurar original', self.reset).pack(fill='x', pady=(0, 7))
        self._button(sidebar, 'Salvar resultado selecionado', self.save_result).pack(fill='x')
        content = tk.Frame(main, bg=_BG)
        content.pack(side='left', fill='both', expand=True)
        top = tk.Frame(content, bg=_BG)
        top.pack(fill='x', pady=(0, 10))
        self._label(top, 'Visualização', 16, bold=True).pack(side='left')
        self.status = self._label(top, 'Carregue uma imagem para começar', 9, _MUTED)
        self.status.pack(side='right')
        panes = tk.PanedWindow(content, orient='horizontal', bg=_BG, sashwidth=7, relief='flat', bd=0)
        panes.pack(fill='both', expand=True)
        self.left_view = self._image_panel(panes, 'ORIGINAL')
        self.right_view = self._image_panel(panes, 'RESULTADO')
        panes.add(self.left_view, minsize=250)
        panes.add(self.right_view, minsize=250)
        bottom = tk.Frame(content, bg=_BG)
        bottom.pack(fill='x', pady=(14, 0))
        self._label(bottom, 'Resposta exibida:', 10, _MUTED).pack(side='left', padx=(0, 8))
        self.selected_result = ttk.Combobox(bottom, state='readonly', width=39, style='PDI.TCombobox')
        self.selected_result.pack(side='left')
        self.selected_result.bind('<<ComboboxSelected>>', lambda _: self.update_previews())
        self._label(bottom, '', 9, _MUTED).pack(side='right')
        self.bind('<Configure>', self._resize_debounced)
        self._resize_after = None

    def _update_sidebar_scrollregion(self, event=None):
        self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox('all'))

    def _fit_sidebar_width(self, event):
        self.sidebar_canvas.itemconfigure(self.sidebar_window, width=event.width)

    def _scroll_sidebar(self, event):
        px, py = self.winfo_pointerxy()
        sx, sy = self.sidebar_canvas.winfo_rootx(), self.sidebar_canvas.winfo_rooty()
        if not (sx <= px < sx + self.sidebar_canvas.winfo_width()
                and sy <= py < sy + self.sidebar_canvas.winfo_height()):
            return
        if getattr(event, 'num', None) == 4:
            units = -3
        elif event.num == 5:
            units = 3
        else:
            units = -int(event.delta / 120) if event.delta else 0
        self.sidebar_canvas.yview_scroll(units, 'units')

    def _image_panel(self, parent, title):
        panel = tk.Frame(parent, bg=_PANEL)
        self._label(panel, title, 10, _BLUE, True).pack(anchor='w', padx=14, pady=(13, 5))
        label = tk.Label(panel, bg='#0b1220', fg=_MUTED, text='Sem imagem',
                         font=('DejaVu Sans', 11), relief='flat')
        label.pack(fill='both', expand=True, padx=12, pady=(0, 12))
        if title == 'ORIGINAL':
            self.original_preview = label
        else:
            self.result_preview = label
        return panel

    def _change_category(self, event=None):
        opts = OPERATIONS[self.category.get()]
        self.choices.configure(values=opts)
        self.operation.set(opts[0])
        self._configure_parameters()

    def _configure_parameters(self, event=None):
        for child in self.parameters.winfo_children():
            child.destroy()
        op = self.operation.get()
        fields = []
        if op == 'Dissolve uniforme': fields = [('alpha', 'Alfa (0 a 1)')]
        elif op == 'Limiarização': fields = [('limiar', 'Limiar (0 a 255)')]
        elif op == 'Gamma': fields = [('gamma', 'Expoente gamma (> 0)')]
        elif op == 'Contraste adaptativo': fields = [('c', 'Constante c'), ('n', 'Vizinhança n (ímpar)')]
        elif op in ('Filtro da média', 'Filtro da mediana'): fields = [('n', 'Vizinhança n (ímpar)')]
        elif op == 'Aguçamento Laplaciano': fields = [('c', 'Intensidade c')]
        elif op == 'High Boost': fields = [('k', 'Ganho k'), ('n', 'Vizinhança n (ímpar)')]
        elif op == 'Convolução genérica': fields = [('offset', 'Offset'), ('borda', 'Borda (reflect / edge / constant)')]
        for key, label in fields:
            self._label(self.parameters, label, 9, _MUTED).pack(anchor='w', pady=(5, 3))
            tk.Entry(self.parameters, textvariable=self.vars[key], font=('DejaVu Sans', 11),
                     bg='#f8fafc', fg='#0f172a', relief='flat').pack(fill='x', ipady=7)
        if op == 'Convolução genérica':
            self.mask_label.pack(fill='x', anchor='w', pady=(10, 4), before=self.run_button)
            self.mask_box.pack(fill='x', before=self.run_button)
        else:
            self.mask_label.pack_forget()
            self.mask_box.pack_forget()
        self.after_idle(self._update_sidebar_scrollregion)

    def open_primary(self):
        path = filedialog.askopenfilename(title='Abrir imagem principal', filetypes=[
            ('Imagens', '*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp'), ('Todos', '*.*')])
        if not path: return
        try:
            self.original = grayscale(path)
        except Exception as exc:
            messagebox.showerror('Erro ao abrir imagem', str(exc)); return
        self.path = path
        self.filename_label.configure(text=f'{Path(path).name}\n{self.original.shape[1]} × {self.original.shape[0]} pixels')
        self.results = []
        self.selected_result.configure(values=[])
        self.selected_result.set('')
        self.status.configure(text='Imagem carregada · pronta para processar')
        self.update_previews()

    def open_secondary(self):
        path = filedialog.askopenfilename(title='Abrir segunda imagem', filetypes=[
            ('Imagens', '*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp'), ('Todos', '*.*')])
        if not path: return
        try: self.second = grayscale(path)
        except Exception as exc:
            messagebox.showerror('Erro ao abrir imagem', str(exc)); return
        self.status.configure(text=f'Segunda imagem: {Path(path).name}')

    def run_operation(self):
        if self.is_busy: return
        if self.original is None:
            messagebox.showwarning('Selecione uma imagem', 'Abra uma imagem principal antes de aplicar uma operação.'); return
        params = {k: v.get() for k,v in self.vars.items()}
        op = self.operation.get()
        try:
            if op == 'Dissolve uniforme' and not 0 <= float(params['alpha']) <= 1:
                raise ValueError('Alfa deve estar entre 0 e 1.')
            if op == 'Gamma' and float(params['gamma']) <= 0:
                raise ValueError('Gamma deve ser maior que zero.')
            if op == 'Limiarização' and not 0 <= int(params['limiar']) <= 255:
                raise ValueError('O limiar deve estar entre 0 e 255.')
            if op in ['Filtro da média','Filtro da mediana','Contraste adaptativo','High Boost']:
                n = int(params['n'])
                if n < 3 or n % 2 == 0:
                    raise ValueError('O tamanho da vizinhança deve ser ímpar e >= 3.')
            if op.startswith('Dissolve') and self.second is None:
                raise ValueError('Abra uma segunda imagem para o dissolve.')
        except ValueError as exc:
            messagebox.showwarning('Parâmetro inválido', str(exc)); return
        mask = self.mask_box.get('1.0', 'end')
        self.is_busy = True
        self.run_button.configure(state='disabled', text='Processando…')
        self.status.configure(text='Calculando pixels…')
        a = self.original.copy()
        b = self.second.copy() if self.second is not None else None
        def work():
            try:
                data = apply_operation(op, a, b, params, mask)
                self.pending.put(('done', data, op))
            except Exception as exc:
                self.pending.put(('error', str(exc), op))
        threading.Thread(target=work, daemon=True).start()

    def _poll(self):
        try:
            while True:
                kind, data, op = self.pending.get_nowait()
                self.is_busy = False
                self.run_button.configure(state='normal', text='▶   Aplicar operação')
                if kind == 'error':
                    self.status.configure(text='Erro ao processar')
                    messagebox.showerror('Erro de processamento', data)
                else:
                    self.results = data
                    labels = [name for name, _ in data]
                    self.selected_result.configure(values=labels)
                    self.selected_result.current(0)
                    self.status.configure(text=f'{op} - {len(data)} resultado(s)')
                    self.update_previews()
        except queue.Empty:
            pass
        self.after(120, self._poll)

    def update_previews(self):
        self.photo_refs.clear()
        self._preview(self.original_preview, self.original)
        index = self.selected_result.current()
        result = self.results[index][1] if self.results and index >= 0 else None
        self._preview(self.result_preview, result)

    def _preview(self, label, array):
        if array is None:
            label.configure(image='', text='Sem imagem')
            return
        im = Image.fromarray(uint8(array))
        w = max(180, label.winfo_width()-22)
        h = max(160, label.winfo_height()-22)
        im.thumbnail((w,h), Image.Resampling.LANCZOS)
        ref = ImageTk.PhotoImage(im)
        self.photo_refs.append(ref)
        label.configure(image=ref, text='')

    def _resize_debounced(self, event):
        if event.widget is not self: return
        if self._resize_after:
            self.after_cancel(self._resize_after)
        self._resize_after = self.after(180, self.update_previews)

    def save_result(self):
        idx = self.selected_result.current()
        if not self.results or idx < 0:
            messagebox.showinfo('Sem resultado', 'Aplique uma operação antes de salvar.'); return
        (ROOT / 'resultados').mkdir(exist_ok=True)
        path = filedialog.asksaveasfilename(initialdir=str(ROOT / 'resultados'),
            defaultextension='.png', filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg'), ('BMP', '*.bmp')])
        if not path: return
        try:
            Image.fromarray(uint8(self.results[idx][1])).save(path)
            self.status.configure(text=f'Salvo: {Path(path).name}')
        except Exception as exc:
            messagebox.showerror('Falha ao salvar', str(exc))

    def reset(self):
        self.results = []
        self.selected_result.configure(values=[])
        self.selected_result.set('')
        self.status.configure(text='Resultado restaurado')
        self.update_previews()


def main():
    Laboratory().mainloop()

if __name__ == '__main__':
    main()