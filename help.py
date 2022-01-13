from PyQt5 import QtCore, QtGui, QtWidgets
import math
from bitarray import bitarray

def fun1(x, y, z):
    return ((x & y) | (~x & z))

def fun2(x, y, z):
    return (x ^ y ^ z)

def fun3(x, y, z):
    return ((x & y) | (x & z) | (y & z))

def shift_left(num, pos):
    return ((num << pos) | (num >> (32 - pos)))

def modadd(a, b):
    return ((a + b) % pow(2, 32))

def out(reg):
    a = hex(reg)
    a = a[2:]
    if (len(a) != 8):
        k = 8 - len(a)
        for i in range(0, k):
            a = "0" + a

    return a

def ABCD(mas_slov_new):
    A0 = 0x67452301
    B0 = 0xefcdab89
    C0 = 0x98badcfe
    D0 = 0x10325476
    E0 = 0xc3d2e1f0

    for i in range(len(mas_slov_new)//16):
        rabot = mas_slov_new[0:16]
        mas_slov_new = mas_slov_new[16:]

        print('rabot ', rabot)
        rabot_new = []
        for i in range(16):
            rabot_new.append(int.from_bytes(rabot[i].tobytes(), byteorder="big"))

        print('rabot_new ', rabot_new)

        w = []
        for i in range(16):
            w.append(rabot_new[i])
        for i in range(16, 80):
            w.append(shift_left((w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16]) % pow(2, 32), 1))
        print('w ', w)

        A = A0
        B = B0
        C = C0
        D = D0
        E = E0

        for i in range(80):
            if 0 <= i <= 19:
                k = 0x5a827999
                tmpr = fun1(B, C, D)
            elif 20 <= i <= 39:
                k = 0x6ed9eba1
                tmpr = fun2(B, C, D)
            elif 40 <= i <= 59:
                k = 0x8f1bbcdc
                tmpr = fun3(B, C, D)
            elif 60 <= i <= 79:
                k = 0xca62c1d6
                tmpr = fun2(B, C, D)

            print(f"func result = {tmpr}")
            print(f"A shift 5 = {shift_left(A, 5)}")

            tmpr = modadd(tmpr, shift_left(A, 5))
            print(f"tmpr = {tmpr}")
            tmpr = modadd(tmpr, E)
            print(f"tmpr = {tmpr}")
            tmpr = modadd(tmpr, k)
            print(f"tmpr = {tmpr}")
            tmpr = modadd(tmpr, w[i])

            print(f"tmpr = {tmpr}")

            print("before")
            print(E, D, C, B, A)

            E = D
            D = C
            C = shift_left(B, 30)
            B = A
            A = tmpr

            print(E, D, C, B, A)

            s = input()

        A0 = modadd(A0, A)
        B0 = modadd(B0, B)
        C0 = modadd(C0, C)
        D0 = modadd(D0, D)
        E0 = modadd(E0, E)

        print(A0, B0, C0, D0, E0)

    print(A0, B0, C0, D0, E0)
    return A0, B0, C0, D0, E0

def codingsha(mes=None, input_file=None):
    new_text = None
    if input_file:
        new_text = input_file.read()
    elif mes:
        new_text = mes.encode()
        print('input_data ', new_text)

    #шаг 1: выращивание потока
    text_in_bit = bitarray()
    for char in new_text:
        text_in_bit += (bin(char)[2:]).zfill(8)
    print('Текст в битах: ', text_in_bit)
    dlina = len(text_in_bit) % 2**64

    if (len(text_in_bit) % 512 < 448 and len(text_in_bit) % 512 != 448):
        text_in_bit += '1'
        while(len(text_in_bit) % 512 != 448):
            text_in_bit += '0'
        print('Добавление 1: ', text_in_bit)

    elif (len(text_in_bit) % 512 > 447):
        text_in_bit += '1'
        while (len(text_in_bit) % 512 != 511):
            text_in_bit += '0'
        for i in range(448):
            text_in_bit += '0'
        print('Добавление 2: ', text_in_bit)

    #шаг 2: добавление длины сообщения
    lenbit = bitarray()
    bin_dlina = bin(dlina)[2:].zfill(64)
    lenbit += bin_dlina
    print(lenbit)
    text_in_bit += lenbit
    print('Добавление длины сообщения: ', text_in_bit)
    print('Длина = ', len(text_in_bit))

    #шаг 4: вычисление в цикле
    blocks = []
    text2 = text_in_bit

    for i in range(0, len(text_in_bit) // 32):
        new_block = text2[:32]
        blocks.append(new_block)
        text2 = text2[32:]

    A, B, C, D, E = ABCD(blocks)

    # шаг 5: результат вычислений
    str_res = out(A) + out(B) + out(C) + out(D)  + out(E)

    return str_res

def main():

    print(codingsha(mes='hello'))


if __name__ == "__main__":
    main()