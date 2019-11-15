# Distributed matrix multiplication

The algorithm used is Cannon's matrix multiplication algorithm for 2D blocked matrices. We assume that p is a perfect square p=s^2, and that n is divisible by s=sqrt(p), where p is number of available machines, n is the size (n x n) of matrix A and matrix B.

- Client program takes following arguments:

  - matrix size
  - number of available machines
  - upper bound of values to be in the matrix

- Server program takes following arguments

  - Port number

- To use pickle as a serializer:

```
export PYRO_SERIALIZERS_ACCEPTED=serpent,json,marshal,pickle
```

## References

- https://cse.buffalo.edu/faculty/miller/Courses/CSE633/Ortega-Fall-2012-CSE633.pdf
- https://people.eecs.berkeley.edu/~demmel/cs267/lecture11/lecture11.html
