import numpy.matlib
import time
import Pyro4
import sys


class MatrixProcessing:
    def __init__(self):
        self.matrix = None
        self.matrix_a = None
        self.matrix_b = None

    def set_matrix_a(self, new_matrix_a):

        self.matrix_a = new_matrix_a

    def set_matrix_b(self, new_matrix_b):

        self.matrix_b = new_matrix_b

    def get_matrix_a(self):
        return self.matrix_a

    def get_matrix_b(self):
        return self.matrix_b

    def print_matrix(self):
        print(self.matrix)

    def get_c_matrix(self):
        return self.matrix

    def clear_c_matrix(self):
        self.matrix = None

    def multiply(self):
        if self.matrix is None:
            self.matrix = numpy.matlib.dot(self.matrix_a, self.matrix_b)
        else:
            self.matrix = self.matrix + numpy.matlib.dot(self.matrix_a, self.matrix_b)


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "pickle"
    port_id = int(sys.argv[1])
    matrix = MatrixProcessing()
    print("System started at port " + str(port_id) + "!")
    Pyro4.Daemon.serveSimple(
        {matrix: "matrix"},
        # host = sys.argv[1],
        port=port_id,
        ns=False,
    )
    while 1:
        time.sleep(0.1)
