from PIL import Image
import numpy as np

from image import (matriz_image, imagem_resultado)

path1 = "suqui.jpeg"
path2 = "digo.jpeg"

with Image.open(path1) as imagem:
    tamanho = imagem.size

matrizA = matriz_image(path1, tamanho)
matrizB = matriz_image(path2, tamanho)

def coeficiente_uniforme(alpha, matrizA, matrizB):

    if matrizA.shape != matrizB.shape:
        raise ValueError("As imagens devem possuir dimensões equivalentes")

    cruzado_uniforme = (1- alpha) * matrizA  + alpha * matrizB

    resultado = imagem_resultado(cruzado_uniforme)

    return resultado

def coeficiente_nao_uniforme(matrizA, matrizB):

    if matrizA.shape != matrizB.shape:
        raise ValueError("As imagens deem possui padrões equivalente")

    altura, largura = matrizA.shape

    alpha = np.linspace(0,1,largura)

    alpha = np.tile(alpha,(altura,1))

    cruzado_nao_uniforme = (1 - alpha) * matrizA + alpha * matrizB

    resultado = imagem_resultado(cruzado_nao_uniforme)

    return resultado
