import convergence as conv


def test_bound_conv():
    conv.conv_test(lambda x: 1 / x / x, 10, conv.power_bound(-1))


def test_bound_tol():
    conv.conv_test(lambda x: 1 / x, 10, conv.power_bound(-1))
