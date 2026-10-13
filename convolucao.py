
import numpy as np
from PIL import Image
from image import matriz_image


def convolucao(matriz, mascara, offset=0, borda="reflect"):
    matriz_float = matriz.astype(np.float64)
    mascara = np.asarray(mascara, dtype=np.float64)

    if matriz_float.ndim != 2:
        raise ValueError("A imagem deve estar em escala de cinza.")

    if mascara.ndim != 2:
        raise ValueError("A máscara deve ser bidimensional.")

    n, m = mascara.shape

    if n == 0 or m == 0:
        raise ValueError("A máscara deve ter dimensões positivas.")

    if borda not in ("reflect", "edge", "constant"):
        raise ValueError("Tratamento de borda inválido.")

    altura, largura = matriz_float.shape

    antes_y = n // 2
    antes_x = m // 2
    depois_y = n - 1 - antes_y
    depois_x = m - 1 - antes_x

    matriz_padded = np.pad(
        matriz_float,
        ((antes_y, depois_y), (antes_x, depois_x)),
        mode=borda
    )

    resultado = np.zeros(
        (altura, largura), dtype=np.float64
    )

    mascara_invertida = np.flip(mascara, axis=(0, 1))

    for y in range(altura):
        for x in range(largura):

            vizinhanca = matriz_padded[
                y:y + n,
                x:x + m
            ]

            soma = 0.0

            for i in range(n):
                for j in range(m):
                    soma += (
                        vizinhanca[i, j]
                        * mascara_invertida[i, j]
                    )

            resultado[y, x] = soma + offset

    return resultado


def converter_8bits(matriz):
    return np.clip(
        np.rint(matriz), 0, 255
    ).astype(np.uint8)


if __name__ == "__main__":
    matriz = matriz_image("suqui.jpeg")

    mascara = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ], dtype=np.float64) / 9

    resultado = convolucao(
        matriz,
        mascara,
        offset=0,
        borda="reflect"
    )

    imagem = Image.fromarray(converter_8bits(resultado))
    imagem.show()
