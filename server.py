import numpy as np
import Pyro4
import sys
import time
import os

os.environ["PYRO_SERIALIZERS_ACCEPTED"] = "serpent,json,marshal,pickle,dill"


@Pyro4.expose
class MatrixProcessing:
    def __init__(self):
        self.matrix = None
        self.matrix_a = None
        self.matrix_b = None

    def set_matrix_a(self, new_matrix_a):
        self.matrix_a = new_matrix_a
        print(self.matrix_a)

    def set_matrix_b(self, new_matrix_b):
        self.matrix_b = new_matrix_b
        print(self.matrix_b)

    def get_matrix_c(self):
        return self.matrix

    def clear_matrix_c(self):
        self.matrix = None

    def multiply(self):
        if self.matrix is None:
            self.matrix = np.dot(self.matrix_a, self.matrix_b)
        else:
            self.matrix = self.matrix + np.dot(self.matrix_a, self.matrix_b)
        print(self.matrix)


if __name__ == "__main__":
    Pyro4.config.SERIALIZER = "pickle"
    port_id = int(sys.argv[1])
    matrix = MatrixProcessing()
    print("System started at port " + str(port_id) + "!")
    Pyro4.Daemon.serveSimple(
        {matrix: "matrix"}, host="10.100.12.238", port=port_id, ns=False,
    )
    while 1:
        time.sleep(0.1)
