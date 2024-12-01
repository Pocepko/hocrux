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

