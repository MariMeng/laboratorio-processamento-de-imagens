from PIL import Image
import numpy as np

from image import (matriz_image)

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

    print(cruzado_uniforme)

    resultado = np.clip(cruzado_uniforme, 0, 255).astype(np.uint8)

    imagem_resultado = Image.fromarray(resultado, mode="L")
    imagem_resultado.show()

def coeficiente_nao_uniforme(matrizA, matrizB):

    if matrizA.shape != matrizB.shape:
        raise ValueError("As imagens deem possui padrões equivalente")

    altura, largura = matrizA.shape

    alpha = np.linspace(0,1,largura)

    alpha = np.tile(alpha,(altura,1))

    cruzado_nao_uniforme = (1 - alpha) * matrizA + alpha * matrizB

    print(cruzado_nao_uniforme)

    resultado = np.clip(cruzado_nao_uniforme,0,255).astype(np.uint8)

    imagem_resultado = Image.fromarray(resultado, mode="L")
    imagem_resultado.show()

coeficiente_nao_uniforme(matrizA, matrizB)
coeficiente_uniforme(0.5, matrizA, matrizB)
