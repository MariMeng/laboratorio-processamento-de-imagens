
import numpy as np
from PIL import Image
from image import matriz_image


def filtro_media(matriz, n=3):
    if n < 3 or n % 2 == 0:
        raise ValueError("A vizinhança deve ser ímpar e >= 3.")

    matriz_float = matriz.astype(np.float64)

    altura, largura = matriz_float.shape
    raio = n // 2

    matriz_padded = np.pad(
        matriz_float, raio, mode="reflect"
    )

    resultado = np.zeros((altura, largura), dtype=np.float64)

    for y in range(altura):
        for x in range(largura):

            vizinhanca = matriz_padded[
                y:y + n,
                x:x + n
            ]

            soma = np.sum(vizinhanca)

            media = soma / (n * n)

            resultado[y, x] = media

    return np.clip(
        np.rint(resultado), 0, 255
    ).astype(np.uint8)


def filtro_mediana(matriz, n=3):
    if n < 3 or n % 2 == 0:
        raise ValueError("A vizinhança deve ser ímpar e >= 3.")

    altura, largura = matriz.shape
    raio = n // 2

    matriz_padded = np.pad(
        matriz, raio, mode="reflect"
    )

    resultado = np.zeros((altura, largura), dtype=np.uint8)

    for y in range(altura):
        for x in range(largura):

            vizinhanca = matriz_padded[
                y:y + n,
                x:x + n
            ]

            valores = vizinhanca.flatten()

            valores_ordenados = np.sort(valores)

            indice_central = len(valores_ordenados) // 2

            mediana = valores_ordenados[indice_central]

            resultado[y, x] = mediana

    return resultado


if __name__ == "__main__":
    matriz = matriz_image("suqui.jpeg")

    media = filtro_media(matriz, n=3)
    mediana = filtro_mediana(matriz, n=3)

    Image.fromarray(media).show()
    Image.fromarray(mediana).show()
