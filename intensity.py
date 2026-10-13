from PIL import Image
import numpy as np
import math
from image import (matriz_image, imagem_resultado)

def negativo(matriz):

    imagem_negativa = 255 - matriz

    resultado = (imagem_negativa).astype(np.uint8)

    imagem_resultado = Image.fromarray(resultado, mode="L")

    return imagem_resultado


def alargamento_constraste(matriz):

    matriz_float = matriz.astype(np.float64)

    rmin = np.min(matriz_float)

    rmax = np.max(matriz_float)

    if rmax == rmin:
        return imagem_resultado(matriz_float)
    else:
        alarg_contraste = ((matriz_float - rmin)/(rmax - rmin) ) * 255

        resultado = imagem_resultado(alarg_contraste)

    return resultado



def limiarizacao(matriz, t):

    nova_imagem = np.where(matriz>=t, 255, 0)

    resultado = imagem_resultado(nova_imagem)

    return resultado


def gamma(matriz, y ):

    gamma_e = 255 * pow((matriz/255.0),y)

    resultado = imagem_resultado(gamma_e)

    return resultado

def logaritmico(matriz):

    matriz_float = matriz.astype(np.float64)

    logaritmico_e  = 255 * ((np.log(1+matriz_float))/(np.log(256)))

    resultado = imagem_resultado(logaritmico_e)

    return resultado
