import numpy as np

from kudi.analysis.numerics import differentiate


def test_differentiate_linear_function():
    x = np.linspace(0.0, 10.0, 6)
    y = 2 * x + 1

    derivative = differentiate(x, y)

    assert derivative.shape == x.shape
    assert np.allclose(derivative, 2.0)
