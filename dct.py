import numpy as np
import math


def compute_lifter_coeffs(lifter, dim):
    coeffs = [0] * dim
    for i in range(0, dim):
        coeffs[i] = 1.0 + 0.5 * lifter * math.sin(math.pi * i / float(lifter))
    return coeffs


def compute_idct_matrix(K, N, cepstral_lifter=0):
    matrix = [[0] * K for i in range(N)]
    # normalizer for X_0
    normalizer = math.sqrt(1.0 / float(N))
    for j in range(0, N):
        matrix[j][0] = normalizer
    # normalizer for other elements
    normalizer = math.sqrt(2.0 / float(N))
    for k in range(1, K):
        for n in range(0, N):
            matrix[n][
                k] = normalizer * math.cos(math.pi / float(N) * (n + 0.5) * k)

    if cepstral_lifter != 0:
        lifter_coeffs = compute_lifter_coeffs(cepstral_lifter, K)
        for k in range(0, K):
            for n in range(0, N):
                matrix[n][k] = float(matrix[n][k]) / lifter_coeffs[k]

    return matrix

def compute_dct_matrix(K, N, cepstral_lifter=0):
    idct_mat = compute_idct_matrix(K,N,cepstral_lifter)
    dct_mat = np.linalg.inv(idct_mat)
    return dct_mat

def compute_dct_matrix2(K, N, cepstral_lifter=0):
    matrix = [[0] * K for i in range(N)]
    trans_matrix = [[0] * N for i in range(K)]
    # normalizer for X_0
    normalizer = math.sqrt(1.0 / float(N))
    for j in range(0, N):
        matrix[j][0] = normalizer
    # normalizer for other elements
    normalizer = math.sqrt(2.0 / float(N))
    for k in range(1, K):
        for n in range(0, N):
            matrix[n][
                k] = normalizer * math.cos(math.pi / float(N) * (n + 0.5) * k)

    for n in range(0, N):
        for k in range(0, K):
            trans_matrix[k][n] = matrix[n][k]

    if cepstral_lifter != 0:
        lifter_coeffs = compute_lifter_coeffs(cepstral_lifter, K)
        for n in range(0, N):
            for k in range(0, K):
                trans_matrix[k][n] = float(trans_matrix[k][n]) * lifter_coeffs[k]

    return trans_matrix


idct = compute_idct_matrix(5, 5, 22)
dct = compute_dct_matrix(5, 5, 22)
dct2 = compute_dct_matrix2(5, 5, 22)
idct = np.array(idct)
dct = np.array(dct)
dct2 = np.array(dct2)
results = idct.dot(dct)
results2 = idct.dot(dct2)
# print(dct)
# print(idct)
print(results)
print(results2)