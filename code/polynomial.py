import random
import copy

MAX_INT = 2 ** 32 - 1
MOD = 4294967311

def bin_pow(a: int, n: int) -> int:
    '''Raising a to the power of n.'''

    res = 1
    while n > 0:
        if n % 2 == 1:
            res *= a
            res %= MOD
        a *= a
        a %= MOD
        n //= 2
    return res


def inverse(a: int) -> int:
    '''Returns modular multiplicative inverse of an integer a
    with respect to the modulus MOD.'''

    return bin_pow(a, MOD - 2)


class Polynomial:
    '''Class of polynomials in the field of the ring of integers modulo MOD'''

    def __init__(self, coefficients=[], rand=False, degree=0) -> None:
        '''Create a polynomial from a list of coefficients
        or a random polynomial if rand is True.'''

        if rand:
            self.coefficients = []
            self.degree = degree
            for i in range(degree + 1):
                self.coefficients.append(random.randint(0, MAX_INT))
        else:
            self.coefficients = coefficients
            self.degree = len(coefficients) - 1

    def __eq__(self, other: 'Polynomial') -> bool:
        return self.coefficients == other.coefficients

    def __call__(self, x: int) -> int:
        '''The value of the polynomial at point x.'''
        res = 0
        x_pow = 1
        for a in self.coefficients:
            res += x_pow * a
            res %= MOD
            x_pow *= x
            x_pow %= MOD
        return res

    def __add__(self, other: 'Polynomial') -> 'Polynomial':
        coefficients = copy.copy(self.coefficients)

        if len(coefficients) < len(other.coefficients):
            coefficients = copy.copy(other.coefficients)
            for i, val in enumerate(self.coefficients):
                coefficients[i] += val
                coefficients[i] %= MOD
            return Polynomial(coefficients)
        else:
            for i, val in enumerate(other.coefficients):
                coefficients[i] += val
                coefficients[i] %= MOD
            return Polynomial(coefficients)


    def __mul__(self, other: 'Polynomial') -> 'Polynomial':
        coefficients_1 = self.coefficients
        coefficients_2 = other.coefficients

        if (self.degree < other.degree):
            coefficients_1, coefficients_2 = coefficients_2, coefficients_1

        coefficients = []

        for i in range(self.degree + other.degree + 1):
            summ = 0
            for j in range(min(i + 1, len(coefficients_2))):
                if i - j >= len(coefficients_1):
                    continue
                summ += coefficients_2[j] * coefficients_1[i - j]
                summ %= MOD
            coefficients.append(summ % MOD)

        return Polynomial(coefficients)


    def get_coefficient(self, ind: int) -> int:
        return self.coefficients[ind]

    def set_coefficient(self, ind: int, x: int) -> None:
        self.coefficients[ind] = x

    def interpolate(x_vals: list[int], y_vals: list[int]) -> 'Polynomial':
        p = Polynomial([0])

        for i in range(len(y_vals)):
            l = Polynomial([1])
            for j in range(len(x_vals)):
                if i != j:
                    l = l * Polynomial([-x_vals[j], 1]) * \
                        Polynomial([inverse(x_vals[i] - x_vals[j])])
            p = p + l * Polynomial([y_vals[i]])

        return p

