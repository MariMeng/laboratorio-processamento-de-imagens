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

    matriz = np.array(imagem_cinza)

    return matriz

def imagem_resultado(matriz):

    resultado = np.clip(matriz, 0, 255).astype(np.uint8)

    imagem_resultado = Image.fromarray(resultado, mode="L")

    return imagem_resultado