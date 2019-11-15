import sys
import time
import math
import Pyro4
import numpy as np
import argparse


class ClientClass:
    def __init__(self, port_number):
        self.block_size = None
        self.port_number = port_number
        self.block_size = None
        self.num_processes = None
        self.s = None

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
        # print(matrix_A)
        # print(matrix_B)
        # print(np.matmul(matrix_A, matrix_B))
        matrices = (matrix_A, matrix_B)
        return matrices

    def skew_shift(self, matrices):
        matrix_A, matrix_B = matrices
        matrix_A_copy = matrix_A.copy()
        matrix_B_copy = matrix_B.copy()
        for i in range(0, self.s):
            for j in range(0, self.s):
                print(f"{i} {j}")
                matrix_A[
                    i * self.block_size : (i + 1) * self.block_size,
                    j * self.block_size : (j + 1) * self.block_size,
                ] = matrix_A_copy[
                    i * self.block_size : (i + 1) * self.block_size,
                    ((j + i) % self.s)
                    * self.block_size : ((j + i) % self.s + 1)
                    * self.block_size,
                ]
                matrix_B[
                    i * self.block_size : (i + 1) * self.block_size,
                    j * self.block_size : (j + 1) * self.block_size,
                ] = matrix_B_copy[
                    ((i + j) % self.s)
                    * self.block_size : ((i + j) % self.s + 1)
                    * self.block_size,
                    j * self.block_size : (j + 1) * self.block_size,
                ]
        matrices = (matrix_A, matrix_B)
        return matrices

    def circular_shift(self, matrices):
        matrix_A, matrix_B = matrices
        matrix_A_copy = matrix_A.copy()
        matrix_B_copy = matrix_B.copy()
        for i in range(0, self.s):
            for j in range(0, self.s):
                matrix_A[
                    i * self.block_size : (i + 1) * self.block_size,
                    j * self.block_size : (j + 1) * self.block_size,
                ] = matrix_A_copy[
                    i * self.block_size : (i + 1) * self.block_size,
                    ((j + 1) % self.s)
                    * self.block_size : ((j + 1) % self.s + 1)
                    * self.block_size,
                ]
                matrix_B[
                    i * self.block_size : (i + 1) * self.block_size,
                    j * self.block_size : (j + 1) * self.block_size,
                ] = matrix_B_copy[
                    ((i + 1) % self.s)
                    * self.block_size : ((i + 1) % self.s + 1)
                    * self.block_size,
                    j * self.block_size : (j + 1) * self.block_size,
                ]
        matrices = (matrix_A, matrix_B)
        return matrices

    def start(self, matrix_size, num_processes, generate_to, remotes):
        self.block_size = int(matrix_size / int(math.sqrt(num_processes)))
        self.s = int(math.sqrt(num_processes))
        self.num_processes = int(num_processes)
        matrices = self.matrix_generation(matrix_size, generate_to)
        t = 0
        remote_num = 0
        while t != int(math.sqrt(self.num_processes)):
            if t == 0:
                matrix_A, matrix_B = self.skew_shift(matrices)
            else:
                matrix_A, matrix_B = self.circular_shift(matrices)
            for i in range(0, self.num_processes):
                for j in range(0, self.num_processes):
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
        for i in range(0, self.num_processes):
            for j in range(0, self.num_processes):
                matrix[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = remotes[remote_num].get_matrix_c()
                remotes[remote_num].clear_matrix_c()
                remote_num = remote_num + 1

        print(matrix)

        return matrix


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "pickle"
    parser = argparse.ArgumentParser(description="Distributed matrix multiplication")
    parser.add_argument(
        "--matrix_size", "-n", default=16, type=int, help="size of the matrix (nxn)"
    )
    parser.add_argument(
        "--numMachines", "-m", default=1, type=int, help="number of available machines"
    )
    parser.add_argument(
        "--generate_to",
        "-u",
        default=8,
        type=int,
        help="upper bound for the values in the matrix",
    )
    args = parser.parse_args()
    matrix_size = int(args.matrix_size)
    machineNumber = int(args.numMachines)
    generate_to = int(args.generate_to)
    remote_urls = [
        # "PYRO:matrix@10.100.11.10:",
        # "PYRO:matrix@192.168.9.98:",
        "PYRO:matrix@10.100.12.238:",  # raghu
        # "PYRO:matrix@192.168.9.208:",
    ]
    client = ClientClass(9601)
    # client.num_processes = int(machineNumber)
    # client.block_size = int(matrix_size / int(math.sqrt(machineNumber)))
    # client.s = int(math.sqrt(machineNumber))
    # matrices = client.matrix_generation(matrix_size, generate_to)
    # print(matrices)
    # matrices = client.skew_shift(matrices)
    # matrices = client.circular_shift(matrices)
    # print(matrices)

    if matrix_size % math.sqrt(machineNumber) == 0:
        client = ClientClass(9601)
        remotes = client.create_remote_objects(remote_urls)
        client.start(matrix_size, machineNumber, generate_to, remotes)
    else:
        print("Square root of machines count must be an integer!")

