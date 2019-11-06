import numpy.matlib
import random
import sys
import time
import math
import Pyro4
import numpy as np


class ClientClass:
    def __init__(self, port_number):
        self.block_size = None
        self.port_number = port_number
        self.block_size = None

    def create_remote_objects(self, remote_urls):
        remotes = []
        for remote_url in remote_urls:
            url = remote_url + str(self.port_number)
            matrix = Pyro4.Proxy(url)
            remotes.append(matrix)
        return remotes

    def matrix_generation(self, matrix_size, generate_to):
        """Generating random matrices of size (matrix_size, matrix_size)"""
        matrix_A = np.random.randint(generate_to, size=(matrix_size, matrix_size))
        matrix_B = np.random.randint(generate_to, size=(matrix_size, matrix_size))
        matrices = (matrix_A, matrix_B)
        return matrices

    def skew_shift(self, matrices):
        matrix_A, matrix_B = matrices
        matrix_A_copy = matrix_A.copy()
        matrix_B_copy = matrix_B.copy()
        for i in range(0, self.block_size):
            for j in range(0, self.block_size):
                matrix_A[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = matrix_A_copy[
                    i : (i + 1) * self.block_size,
                    (j + i)
                    % self.block_size : ((j + i) % self.block_size + 1)
                    * self.block_size,
                ]

                matrix_B[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = matrix_B_copy[
                    (i + j)
                    % self.block_size : ((i + j) % self.block_size + 1)
                    * self.block_size,
                    j : (j + 1) * self.block_size,
                ]
        matrices = (matrix_A, matrix_B)
        return matrices

    def circular_shift(self, matrices):
        matrix_A, matrix_B = matrices
        matrix_A_copy = matrix_A.copy()
        matrix_B_copy = matrix_B.copy()
        for i in range(0, self.block_size):
            for j in range(0, self.block_size):
                matrix_A[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = matrix_A_copy[
                    i : (i + 1) * self.block_size,
                    (j + 1)
                    % self.block_size : ((j + 1) % self.block_size + 1)
                    * self.block_size,
                ]

                matrix_B[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = matrix_B_copy[
                    (i + 1)
                    % self.block_size : ((i + 1) % self.block_size + 1)
                    * self.block_size,
                    j : (j + 1) * self.block_size,
                ]
        matrices = (matrix_A, matrix_B)
        return matrices

    def start(self, matrix_size, num_processes, generate_to, remotes):
        self.block_size = int(math.sqrt(num_processes))
        matrices = self.matrix_generation(matrix_size, generate_to)
        t = 0
        remote_num = 0
        while t != self.block_size:
            if t == 0:
                matrix_A, matrix_B = self.skew_shift(matrices)
            else:
                matrix_A, matrix_B = self.circular_shift(matrices)
            for i in range(0, self.block_size):
                for j in range(0, self.block_size):
                    remotes[remote_num].set_matrix_a(
                        matrix_A[
                            i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                        ]
                    )
                    remotes[remote_num].set_matrix_b(
                        matrix_B[
                            i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                        ]
                    )
                    remotes[remote_num].multiply()
                    remote_num = remote_num + 1
            t = t + 1
        matrix = np.zeros(shape=(matrix_size, matrix_size))
        remote_num = 0
        for i in range(0, self.block_size):
            for j in range(0, self.block_size):
                matrix[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = remotes[remote_num].get_matrix_c()
                remote_num = remote_num + 1

        print(matrix)

        return matrix


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "pickle"
    start_time = time.time()
    matrix_size = int(sys.argv[1])
    machineNumber = float(sys.argv[2])
    generate_to = int(sys.argv[3])
    remote_urls = ["PYRO:matrix@localhost:"]
    if machineNumber.is_integer() and matrix_size % math.sqrt(machineNumber) == 0:
        client = ClientClass(9601)
        remotes = client.create_remote_objects(remote_urls)
        client.start(matrix_size, machineNumber, generate_to, remotes)
    else:
        print("Square root of machines count must be an integer!")

