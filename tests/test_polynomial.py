from code.polynomial import Polynomial

def test_arithmetic():
    p1 = Polynomial([1, 1])
    p2 = Polynomial([1, 2, 3])
    p3 = Polynomial([2, 3, 3])
    assert p1 + p2 == p3
    assert p2 + p1 == p3

    p3 = Polynomial([1, 3, 5, 3])
    assert p1 * p2 == p3
    assert p2 * p1 == p3


def test_call():
    p = Polynomial(rand=True, degree=0)
    assert p(1) == p(0)

    p = Polynomial([1, 2, 1])
    assert p(0) == 1
    assert p(1) == 4


def test_interpolate():
    p1 = Polynomial([1, 2, 1])

    x = [0, 1, 2]
    y = [p1(0), p1(1), p1(2)]

    p2 = Polynomial.interpolate(x, y)

    assert p1 == p2

def test_coefficient():
    p = Polynomial(rand=True, degree=1)

    p.set_coefficient(0, 1)
    p.set_coefficient(1, 2)

    assert p.get_coefficient(0) == 1
    assert p.get_coefficient(1) == 2

