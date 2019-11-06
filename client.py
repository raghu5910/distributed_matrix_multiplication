import numpy.matlib
import random
import sys
import time
import math
import Pyro4
import numpy as np


class ClientClass:
    def __init__(self, port_number):
        self.array = None
        self.block_count = None
        self.block_size = None
        self.servers = None
        self.machine_number = 0
        self.port_number = port_number
        self.machine_count = 0

    def get_result_matrix(self):
        result = []
        for element in self.array:
            temp = None
            for arr in element:
                if temp is None:
                    temp = arr.get_c_matrix()
                    print(temp)
                else:
                    matrix = arr.get_c_matrix()
                    temp = numpy.append(temp, matrix, axis=1)
            result.append(temp)
        # result = numpy.append(*result, axis=0)
        print(temp)

    def run(self, machine_number, generator_from, generator_to):
        self.servers = [
            "PYRO:matrix@localhost:",
            # "PYRO:matrix@someotherserver.org:",
        ]
        machine_number = int(machine_number)
        self.block_size = int(array_size / machine_number)
        self.block_count = int(array_size / self.block_size)
        # numpy.set_printoptions(threshold=numpy.nan)
        matrices = self.generate_matrices(array_size, generator_from, generator_to)
        matrices = (self.split_matrix(matrices[0]), self.split_matrix(matrices[1]))
        # Pyro4.config.SERIALIZER = "pickle"
        self.cannons_algorithm(matrices)
        self.get_result_matrix()
        print("--- %s seconds ---" % (time.time() - start_time))

    def split_matrix(self, input_matrix):
        result_matrix = []
        for x in range(0, self.block_count):
            temporary_array = []
            for y in range(0, self.block_count):
                x_value = int(self.block_size * x)
                x_second_value = int(self.block_size * (x + 1))
                y_value = int(self.block_size * y)
                y_second_value = int(self.block_size * (y + 1))
                temporary_array.append(
                    input_matrix[x_value:x_second_value, y_value:y_second_value]
                )
            result_matrix.append(temporary_array)
        return result_matrix

    def generate_matrices(self, array_size, generator_from, generator_to):
        matrix_a = numpy.matlib.matrix(
            self.generate_matrix(array_size, generator_from, generator_to)
        )
        matrix_b = numpy.matlib.matrix(
            self.generate_matrix(array_size, generator_from, generator_to)
        )
        return matrix_a, matrix_b

    def skew_matrix(self, matrices):
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
                matrix_A, matrix_B = self.skew_matrix(matrices)
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
        matrix = np.zeros(shape=(array_size, array_size))
        remote_num = 0
        for i in range(0, self.block_size):
            for j in range(0, self.block_size):
                matrix[
                    i : (i + 1) * self.block_size, j : (j + 1) * self.block_size
                ] = remotes[remote_num].get_c_matrix()
                remote_num = remote_num + 1

        print(matrix)

        return matrix

    def matrix_generation(self, matrix_size, generate_to):
        """Generating random matrices of size (matrix_size, matrix_size)"""
        matrix_A = np.random.randint(generate_to, size=(matrix_size, matrix_size))
        matrix_B = np.random.randint(generate_to, size=(matrix_size, matrix_size))
        matrices = (matrix_A, matrix_B)
        return matrices

    @staticmethod
    def generate_matrix(array_size, generate_from, generator_to):
        result = ""
        for _ in range(0, array_size):
            for _ in range(0, array_size):
                result += str(random.randint(0, generator_to)) + ","
            result = result[:-1] + ";"
        return result[:-1]

    def cannons_algorithm(self, matrices):
        self.array = []
        self.set_initial_matrices(matrices)
        self.skew(self.block_count)
        for _ in range(0, self.machine_number):
            for element in self.array:
                for value in element:
                    value.multiply()
                    print(value.get_c_matrix())
            self.shift_a_matrix_left()
            self.shift_b_matrix_up(self.block_count)

    def set_initial_matrices(self, matrices):
        for x in range(0, self.block_count):
            temp_array = []
            for y in range(0, self.block_count):
                url = self.servers[self.machine_count % 2] + str(self.port_number)
                matrix = Pyro4.Proxy(url)
                matrix.clear_c_matrix()
                matrix.set_matrix_a(matrices[0][x][y])
                matrix.set_matrix_b(matrices[1][x][y])
                # print(matrix.get_matrix_a())
                # matrix.multiply()
                # print(matrix.get_c_matrix())
                temp_array.append(matrix)
                self.machine_count += 1
                if self.machine_count % 2 == 0:
                    self.port_number += 1
            self.array.append(temp_array)
            # print(self.array)

    def skew(self, vector_length):
        for i in range(1, vector_length):
            current_element = self.array[0][i].get_matrix_b()
            for element in reversed(self.array):
                temp = element[i].get_matrix_b()
                element[i].set_matrix_b(current_element)
                current_element = temp
        for i in range(1, vector_length):
            current_element = self.array[i][0].get_matrix_a()
            for el in reversed(self.array[i]):
                temp = el.get_matrix_a()
                el.set_matrix_a(current_element)
                current_element = temp

    def shift_a_matrix_left(self):
        for element in self.array:
            current_element = element[0].get_matrix_a()
            for el in reversed(element):
                temp = el.get_matrix_a()
                el.set_matrix_a(current_element)
                current_element = temp

    def shift_b_matrix_up(self, block_count):
        for i in range(0, block_count):
            current_element = self.array[0][i].get_matrix_b()
            for element in reversed(self.array):
                temp = element[i].get_matrix_b()
                element[i].set_matrix_b(current_element)
                current_element = temp


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "pickle"
    start_time = time.time()
    machineNumber = float(sys.argv[1])
    machineNumber = math.sqrt(machineNumber)
    array_size = int(sys.argv[2])
    if machineNumber.is_integer() and array_size % machineNumber == 0:
        client = ClientClass(9601)
        client.run(machineNumber, int(sys.argv[3]), int(sys.argv[4]))
    else:
        print("Square root of machines count must be an integer!")

