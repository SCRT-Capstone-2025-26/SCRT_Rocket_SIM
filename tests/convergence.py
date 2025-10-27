import numpy as np


def power_bound(power, tol=0.3):
    def fun(value):
        return (value**power) + tol

    return fun


def conv_test(fun, steps, bound_fun):
    values = range(1, steps + 1)

    data = np.array([fun(value) for value in values])

    data -= data[-1]
    data = abs(data)
    max_data = max(data)
    if max_data != 0:
        data /= max(data)

    assert (data <= np.array([bound_fun(value) for value in values])).all()
