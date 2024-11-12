import argparse
import pickle
import random
import copy
import os

class IntData:
    '''
    def __init__(self, data):
        self.bytes_count = len(data)
        self.numbers = []
        for i in range(0, len(data), 4):
            self.numbers.append(int.from_bytes(data[i:i + 4],
                                byteorder='little'))
    '''

    def __init__(self, path):
        self.x_val = 0
        with open(path, mode="rb") as file:
            data = file.read()
            self.bytes_count = len(data)
            self.numbers = []
            for i in range(0, len(data), 4):
                self.numbers.append(int.from_bytes(data[i:i + 4],
                                    byteorder='little'))


    def to_bytes(self):
        res = bytes()
        bytes_list = []
        for i in range(len(self.numbers) - 1):
            bytes_list.append(self.numbers[i].to_bytes(4, byteorder='little'))
        n = len(self.numbers) - 1

        bytes_list.append(self.numbers[-1].to_bytes(self.bytes_count - n * 4,
        #bytes_list.append(self.numbers[-1].to_bytes(4,

                                                    byteorder='little'))
        res = res.join(bytes_list)
        return res

    def get_int(self, ind):
        return self.numbers[ind]

    def set_int(self, ind, val):
        self.numbers[ind] = val

    def get_ints(self):
        return self.numbers

    def get_x_val(self):
        return self.x_val

    def set_x_val(self, val):
        self.x_val = val

    def write(self):
        print(f'bytes_count = {self.bytes_count}')
        print(f'x_val = {self.x_val}')
        for i in self.numbers:
            print(i)
        print()

'''
def read_file(path):
    with open(path, mode="rb") as file:
        data = file.read()
    data = FileData(data)
    return data
'''

'''
def write_file(path, data):
    with open(path, mode="wb") as file:
        file.write(data.to_bytes())
'''

# 2^32 - 1 = 4294967295
# 4294967311
# polynomial

MAX_INT = 2 ** 32 - 1
MOD = 4294967311

def bin_pow(a, n):
    res = 1
    while n > 0:
        if n % 2 == 1:
            res *= a
            res %= MOD
        a *= a
        a %= MOD
        n //= 2
    return res


def inverse(a):
    return bin_pow(a, MOD - 2)


class Polynomial:

    def __init__(self, coefficients=[], rand=False, degree=0):
        if rand:
            self.coefficients = []
            self.degree = degree
            for i in range(degree + 1):
                self.coefficients.append(random.randint(0, MAX_INT))
        else:
            self.coefficients = coefficients
            self.degree = len(coefficients) - 1

    def __call__(self, x):
        res = 0
        x_pow = 1
        for a in self.coefficients:
            res += x_pow * a
            res %= MOD
            x_pow *= x
            x_pow %= MOD
        return res

    def __add__(self, other):
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


    def __mul__(self, other):
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


    def get_coefficient(self, ind):
        return self.coefficients[ind]

    def set_coefficient(self, ind, x):
        self.coefficients[ind] = x

    def interpolate(x_vals, y_vals):
        p = Polynomial([0])

        for i in range(len(y_vals)):
            l = Polynomial([1])
            for j in range(len(x_vals)):
                if i != j:
                    l = l * Polynomial([-x_vals[j], 1]) * Polynomial([inverse(x_vals[i] - x_vals[j])])
            p = p + l * Polynomial([y_vals[i]])

        return p


def split(data, n, threshold):

    polynomials = []

    for i in range(len(data.get_ints())):
        p = Polynomial(rand=True, degree=threshold - 1)
        p.set_coefficient(0, data.get_int(i))
        polynomials.append(p)

    parts = []

    for i in range(n):
        part = copy.deepcopy(data)
        numbers = part.get_ints()
        for j in range(len(data.get_ints())):
            part.set_int(j, polynomials[j](i + 1))
            #print(i + 1, j, polynomials[j](i + 1))
        part.set_x_val(i + 1)
        parts.append(part)

    return parts


def split_command(path, n, threshold):

    data = IntData(path)

    parts = split(data, n, threshold)

    path_parts = path.split('/')
    file_name = path_parts[-1]
    dirr = '/'.join(path_parts[:-1])

    pref = file_name
    suf = ''

    if '.' in file_name:
        name_parts = file_name.split('.')
        suf = name_parts[-1]
        pref = '.'.join(name_parts[:-1])

    for i, part in enumerate(parts):
        new_path = ""
        if len(dirr) > 0:
            new_path = dirr + '/' + pref + str(i + 1) + '.' + suf
        else:
            new_path = pref + str(i + 1) + '.' + suf
        #part.write()
        with open(new_path, 'wb') as file:
            pickle.dump(part, file)
        #write_file(new_path, data)


def bind(parts, threshold):

    data = copy.copy(parts[0])

    for i in range(len(data.get_ints())):
        x_vals = []
        y_vals = []
        for part in parts:
            x_vals.append(part.get_x_val())
            y_vals.append(part.get_int(i))

        p = Polynomial.interpolate(x_vals, y_vals)

        data.set_int(i, p.get_coefficient(0))

    return data


def bind_command(path, threshold):

    path_parts = path.split('/')
    file_pref = path_parts[-1]
    dirr = '/'.join(path_parts[:-1])

    parts = []

    if len(dirr) == 0:
        dirr = '.'

    with os.scandir(dirr) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith(file_pref):
                with open(dirr + '/' + entry.name, 'rb') as file:
                    parts.append(pickle.load(file))

    '''
    for part in parts:
        part.write()
    '''

    if len(parts) < threshold:
        print("Parts less than threshold")
        sys.exit(1)

    data = bind(parts[:threshold], threshold)

    with open(path, mode="wb") as file:
        file.write(data.to_bytes())


def test_copy(path):
    data = IntData(path)

    with open(path + '2', 'wb') as file:
        pickle.dump(data, file)

    with open(path + '2', 'rb') as file:
        data = pickle.load(file)

    with open(path + '3', mode="wb") as file:
        file.write(data.to_bytes())



parser = argparse.ArgumentParser(description="Splitting a file into several" \
                                             "parts and restoring it using " \
                                             "Shamir's scheme.")

parser.add_argument("command", type=str, help="Command to execute (split or" \
                    " bind)")
parser.add_argument("path", type=str, help="Path to file to split or prefix" \
                    " of files to bind")
parser.add_argument("-n", type=int, default=0, help="Number of parts that "  \
                                                    "will be created")
parser.add_argument("t", type=int, help="Number of parts required for "      \
                                        "restoration (threshold)")

args = parser.parse_args()

match args.command:
    case "test":
        test_copy(args.path)
    case "bind":
        if 1 < args.t:
            bind_command(args.path, args.t)
        else:
            print("The threshold must be greater than one")
    case "split":
        if 1 < args.t and args.t <= args.n:
            split_command(args.path, args.n, args.t)
        else:
            print("The threshold must be greater than one and less than or " \
                  "equal to the number of parts")
    case _:
        print(f"Unknown command '{args.command}', use 'split' or 'bind'");

