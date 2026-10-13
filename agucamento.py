
import numpy as np
from PIL import Image

from image import matriz_image
from convolucao import convolucao, converter_8bits


def agucamento_laplaciano(matriz, c=1):
    if c < 0:
        raise ValueError("A constante c deve ser não negativa.")

    matriz_float = matriz.astype(np.float64)

    mascara = np.array([
        [0, 1, 0],
        [1, -4, 1],
        [0, 1, 0]
    ])

    resposta_laplaciano = convolucao(
        matriz_float,
        mascara,
        offset=0
    )

    imagem_agucada = (
        matriz_float - c * resposta_laplaciano
    )

    return {
        "laplaciano": resposta_laplaciano,
        "agucada": imagem_agucada
    }



def high_boost(matriz, k=1.5, n=3):
    if k < 0:
        raise ValueError("O fator k deve ser não negativo.")

    if n < 3 or n % 2 == 0:
        raise ValueError("A vizinhança deve ser ímpar e >= 3.")

    matriz_float = matriz.astype(np.float64)

    mascara_media = np.ones(
        (n, n), dtype=np.float64
    ) / (n * n)

    imagem_suavizada = convolucao(
        matriz_float,
        mascara_media,
        offset=0
    )

    mascara_detalhes = (
        matriz_float - imagem_suavizada
    )

    imagem_agucada = (
        matriz_float + k * mascara_detalhes
    )

    return {
        "suavizada": imagem_suavizada,
        "detalhes": mascara_detalhes,
        "agucada": imagem_agucada
    }



def mostrar_imagem(matriz):
    imagem = Image.fromarray(converter_8bits(matriz))
    imagem.show()


def mostrar_resposta_assinada(matriz):

    maior = np.max(np.abs(matriz))

    if maior == 0:
        visualizacao = np.full(
            matriz.shape, 128, dtype=np.uint8
        )
    else:
        visualizacao = 128 + 127 * (matriz / maior)
        visualizacao = converter_8bits(visualizacao)

    Image.fromarray(visualizacao).show()



if __name__ == "__main__":
    matriz = matriz_image("suqui.jpeg")

    resultado_laplaciano = agucamento_laplaciano(
        matriz, c=1
    )

    print("Imagem original")
    mostrar_imagem(matriz)

    print("Resposta Laplaciana")
    mostrar_resposta_assinada(
        resultado_laplaciano["laplaciano"]
    )

    print("Imagem aguçada pelo Laplaciano")
    mostrar_imagem(
        resultado_laplaciano["agucada"]
    )

    resultado_highboost = high_boost(
        matriz, k=1.5, n=3
    )

    print("Imagem suavizada")
    mostrar_imagem(
        resultado_highboost["suavizada"]
    )

    print("Detalhes extraídos")
    mostrar_resposta_assinada(
        resultado_highboost["detalhes"]
    )

    print("Imagem aguçada pelo High Boost")
    mostrar_imagem(
        resultado_highboost["agucada"]
    )
