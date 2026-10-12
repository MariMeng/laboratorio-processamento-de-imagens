from PIL import Image
import numpy as np
from pathlib import Path

def matriz_image(path, tamanho=None):
    imagem = Image.open(path)

    imagem_cinza = imagem.convert("L")

    if tamanho is not None:
        imagem_cinza = imagem_cinza.resize(tamanho)

    nome = Path(path).stem
    extensao = Path(path).suffix

    caminho_saida = Path("resultados") / f"{nome}_cinza{extensao}"
    imagem_cinza.save(caminho_saida)

    matriz = np.array(imagem_cinza)

    return matriz