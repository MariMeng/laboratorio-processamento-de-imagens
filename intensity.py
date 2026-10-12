from PIL import Image
import numpy as np
from image import (matriz_image)

path = 'suqui.jpeg'

with Image.open(path) as imagem:
    tamanho = imagem.size

matriz = matriz_image(path, tamanho)

def negativo(matriz):

    imagem_negativa = 255 - matriz

    resultado = (imagem_negativa).astype(np.uint8)

    imagem_resultado = Image.fromarray(resultado, mode="L")

    imagem_resultado.show()

    return imagem_resultado

negativo(matriz)



