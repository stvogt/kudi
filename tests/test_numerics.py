import numpy as np
import pytest

from kudi.analysis.numerics import differentiate


def test_differentiate_linear_function():
    x = np.linspace(0.0, 10.0, 6)
    y = 2 * x + 1

    derivative = differentiate(x, y)

    assert derivative.shape == x.shape
    assert np.allclose(derivative, 2.0)


def test_differentiate_quadratic_captures_endpoints():
    x = np.linspace(-2.0, 2.0, 5)
    y = x**2

    derivative = differentiate(x, y)

    assert derivative.shape == x.shape
    assert derivative[0] == pytest.approx(-4.0)
    assert derivative[-1] == pytest.approx(4.0)
    assert derivative[2] == pytest.approx(0.0)


def test_differentiate_rejects_non_monotonic_coordinates():
    x = np.array([0.0, 1.0, 0.5])
    y = np.array([0.0, 1.0, 0.25])

    with pytest.raises(ValueError, match="monotonic"):
        differentiate(x, y)
