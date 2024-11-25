import argparse
import pickle
import random
import copy
import os

from polynomial import Polynomial


class IntData:
    '''This class stores file data as a list of four byte numbers
    and associated information for later file recovery.'''

    def __init__(self, path: str) -> None:
        self.x_val = 0
        with open(path, mode="rb") as file:
            data = file.read()
            self.bytes_count = len(data)
            self.numbers = []
            for i in range(0, len(data), 4):
                self.numbers.append(int.from_bytes(data[i:i + 4],
                                    byteorder='little'))

    def to_bytes(self) -> bytes:
        '''This method restores the contents of the file in binary form.'''

        res = bytes()
        bytes_list = []
        for i in range(len(self.numbers) - 1):
            bytes_list.append(self.numbers[i].to_bytes(4, byteorder='little'))
        n = len(self.numbers) - 1

        bytes_list.append(self.numbers[-1].to_bytes(self.bytes_count - n * 4,
                                                    byteorder='little'))
        res = res.join(bytes_list)
        return res

    def get_int(self, ind: int) -> int:
        return self.numbers[ind]

    def set_int(self, ind: int, val: int) -> None:
        self.numbers[ind] = val

    def get_ints(self) -> list[int]:
        return self.numbers

    def get_x_val(self) -> int:
        return self.x_val

    def set_x_val(self, val: int) -> None:
        self.x_val = val


def split(data: IntData, n: int, threshold: int) -> list[IntData]:
    '''Apply the Shamir's scheme and divide the file into parts.'''

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
        part.set_x_val(i + 1)
        parts.append(part)

    return parts


def split_path(path: str) -> tuple[str, str]:
    path_parts = path.split('/')
    file_name = path_parts[-1]
    dirr = '/'.join(path_parts[:-1])

    if len(dirr) == 0:
        dirr = '.'

    return (dirr, file_name)


def split_file_name(file_name: str) -> tuple[str, str]:
    pref = file_name
    suf = ''

    if '.' in file_name:
        name_parts = file_name.split('.')
        suf = name_parts[-1]
        pref = '.'.join(name_parts[:-1])

    return (pref, suf)


def split_command(path: str, n: int, threshold: int) -> None:

    data = IntData(path)

    parts = split(data, n, threshold)

    dirr, file_name = split_path(path)

    pref, suf = split_file_name(file_name)

    for i, part in enumerate(parts):
        new_path = ""
        if len(dirr) > 0:
            new_path = dirr + '/' + pref + str(i + 1) + '.' + suf
        else:
            new_path = pref + str(i + 1) + '.' + suf
        with open(new_path, 'wb') as file:
            pickle.dump(part, file)


def bind(parts: list[IntData], threshold: int) -> IntData:
    '''Using the Shamir's scheme to merge the parts'''

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


def bind_command(path: str, threshold: int) -> None:

    dirr, file_pref = split_path(path)

    parts = []

    file_suf = ''

    with os.scandir(dirr) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.startswith(file_pref):
                file_suf = split_file_name(entry.name)[1]
                with open(dirr + '/' + entry.name, 'rb') as file:
                    parts.append(pickle.load(file))

    if len(parts) < threshold:
        print("Parts less than threshold")
        sys.exit(1)

    data = bind(parts[:threshold], threshold)

    if (len(file_suf) > 0):
        path += '.' + file_suf

    with open(path, mode="wb") as file:
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

