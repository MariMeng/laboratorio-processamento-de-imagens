import numpy as np


def contraste_adaptativo(matriz, c=10.0, n=3, epsilon=1.0):

    if not isinstance(n, int) or n < 3 or n % 2 == 0:
        raise ValueError('A vizinhança deve ser ímpar e maior ou igual a 3.')
    
    if c < 0 or epsilon <= 0:
        raise ValueError('c deve ser não negativo e epsilon positivo.')
    
    origem = np.asarray(matriz, dtype=np.float64)

    if origem.ndim != 2:
        raise ValueError('É necessária uma imagem em tons de cinza.')
    raio = n // 2

    extendida = np.pad(origem, raio, mode='reflect')
    saida = np.empty_like(origem)

    for y in range(origem.shape[0]):
        for x in range(origem.shape[1]):
            janela = extendida[y:y+n, x:x+n]
            media = np.sum(janela) / (n*n)
            variancia = np.sum((janela-media)**2) / (n*n)
            desvio = np.sqrt(variancia)
            saida[y,x] = media + c * (origem[y,x]-media)/(desvio+epsilon)

    return np.clip(np.rint(saida), 0, 255).astype(np.uint8)
