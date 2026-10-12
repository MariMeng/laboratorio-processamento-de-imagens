from PIL import Image

import numpy as np
from image import (matriz_image, imagem_resultado)

path = 'suqui.jpeg'

matriz = matriz_image(path)

def histograma_expansao(matriz):


    matriz_float = matriz.astype(np.float64)

    r_min = np.min(matriz_float)
    r_max = np.max(matriz_float)

    if r_max == r_min:
        matriz_expansao = matriz_float
    else:
        matriz_expansao = ((matriz_float - r_min) / (r_max - r_min)) * 255

    resultado = imagem_resultado(matriz_expansao)

    resultado.show()

    return resultado


def histograma_equalizacao(matriz):
    pixel = [0] * 256

    for linha in matriz:
        for intensidade in linha:
            pixel[intensidade] +=1

    frequencia_relativa = [0] * 256

    total_pixels = matriz.size

    for i in range(256):
        frequencia_relativa[i] = pixel[i]/total_pixels

    frequencia_acumulada = [0] * 256

    soma = 0

    for i in range(256):
        soma += frequencia_relativa[i]
        frequencia_acumulada[i] = soma

    print("Total de pixels:", matriz.size)
    print("Soma das frequências:", sum(pixel))
    print("Frequência acumulada final:", frequencia_acumulada[-1])

    equalizacao = np.round(
        255 * np.array(frequencia_acumulada)
    )

    matriz_equalizacao = equalizacao[matriz]

    matriz_equalizacao = np.clip(
        matriz_equalizacao, 0, 255
    ).astype(np.uint8)

    resultado = Image.fromarray(matriz_equalizacao)
    resultado.show()

 

    return resultado

histograma_equalizacao(matriz)


    

    
