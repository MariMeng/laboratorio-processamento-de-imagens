
import numpy as np
from PIL import Image
from image import matriz_image


def aplicar_mascara(matriz, mascara):
    matriz = matriz.astype(np.float64)
    mascara = np.asarray(mascara, dtype=np.float64)

    altura, largura = matriz.shape
    mh, mw = mascara.shape

    pad_y = mh // 2
    pad_x = mw // 2

    matriz_padded = np.pad(
        matriz,
        ((pad_y, pad_y), (pad_x, pad_x)),
        mode="reflect"
    )

    resultado = np.zeros((altura, largura), dtype=np.float64)

    for y in range(altura):
        for x in range(largura):
            vizinhanca = matriz_padded[
                y:y + mh,
                x:x + mw
            ]

            valor = np.sum(vizinhanca * mascara)

            resultado[y, x] = valor

    return resultado


def magnitude_gradiente(gx, gy):
    return np.sqrt(gx ** 2 + gy ** 2)


def visualizar_resposta(matriz):
    valores = np.abs(matriz.astype(np.float64))

    maior = np.max(valores)

    if maior > 0:
        valores = valores * (255.0 / maior)

    return np.rint(valores).astype(np.uint8)


def mostrar(matriz):
    imagem = Image.fromarray(visualizar_resposta(matriz))
    imagem.show()


def roberts(matriz):
    mascara_gx = np.array([
        [1, 0],
        [0, -1]
    ])

    mascara_gy = np.array([
        [0, 1],
        [-1, 0]
    ])

    gx = aplicar_mascara(matriz, mascara_gx)
    gy = aplicar_mascara(matriz, mascara_gy)

    magnitude = magnitude_gradiente(gx, gy)

    return {
        "Gx": gx,
        "Gy": gy,
        "magnitude": magnitude
    }



def sobel(matriz):
    mascara_gx = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ])

    mascara_gy = np.array([
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1]
    ])

    gx = aplicar_mascara(matriz, mascara_gx)
    gy = aplicar_mascara(matriz, mascara_gy)

    magnitude = magnitude_gradiente(gx, gy)

    return {
        "Gx": gx,
        "Gy": gy,
        "magnitude": magnitude
    }


def kirsch(matriz):
    mascara_norte = np.array([
        [5, 5, 5],
        [-3, 0, -3],
        [-3, -3, -3]
    ])

    mascara_nordeste = np.array([
        [-3, 5, 5],
        [-3, 0, 5],
        [-3, -3, -3]
    ])

    mascara_leste = np.array([
        [-3, -3, 5],
        [-3, 0, 5],
        [-3, -3, 5]
    ])

    mascara_sudeste = np.array([
        [-3, -3, -3],
        [-3, 0, 5],
        [-3, 5, 5]
    ])

    mascara_sul = np.array([
        [-3, -3, -3],
        [-3, 0, -3],
        [5, 5, 5]
    ])

    mascara_sudoeste = np.array([
        [-3, -3, -3],
        [5, 0, -3],
        [5, 5, -3]
    ])

    mascara_oeste = np.array([
        [5, -3, -3],
        [5, 0, -3],
        [5, -3, -3]
    ])

    mascara_noroeste = np.array([
        [5, 5, -3],
        [5, 0, -3],
        [-3, -3, -3]
    ])

    mascaras = {
        "Norte": mascara_norte,
        "Nordeste": mascara_nordeste,
        "Leste": mascara_leste,
        "Sudeste": mascara_sudeste,
        "Sul": mascara_sul,
        "Sudoeste": mascara_sudoeste,
        "Oeste": mascara_oeste,
        "Noroeste": mascara_noroeste
    }

    respostas = {}

    for direcao, mascara in mascaras.items():
        respostas[direcao] = aplicar_mascara(
            matriz, mascara
        )

    todas = np.stack(list(respostas.values()))

    bordas = np.max(np.abs(todas), axis=0)

    return {
        "direcoes": respostas,
        "bordas": bordas
    }



def laplaciano(matriz):
    mascara = np.array([
        [0, 1, 0],
        [1, -4, 1],
        [0, 1, 0]
    ])

    resposta = aplicar_mascara(matriz, mascara)

    bordas = np.abs(resposta)

    return {
        "resposta": resposta,
        "bordas": bordas
    }



if __name__ == "__main__":
    matriz = matriz_image("suqui.jpeg")

    resultado_roberts = roberts(matriz)

    print("Roberts - Gx")
    mostrar(resultado_roberts["Gx"])

    print("Roberts - Gy")
    mostrar(resultado_roberts["Gy"])

    print("Roberts - Magnitude")
    mostrar(resultado_roberts["magnitude"])

    resultado_sobel = sobel(matriz)

    print("Sobel - Gx")
    mostrar(resultado_sobel["Gx"])

    print("Sobel - Gy")
    mostrar(resultado_sobel["Gy"])

    print("Sobel - Magnitude")
    mostrar(resultado_sobel["magnitude"])

    resultado_kirsch = kirsch(matriz)

    for direcao, resposta in resultado_kirsch["direcoes"].items():
        print("Kirsch:", direcao)
        mostrar(resposta)

    print("Kirsch - Bordas finais")
    mostrar(resultado_kirsch["bordas"])

    resultado_laplaciano = laplaciano(matriz)

    print("Laplaciano - Resposta")
    mostrar(resultado_laplaciano["resposta"])

    print("Laplaciano - Bordas")
    mostrar(resultado_laplaciano["bordas"])
