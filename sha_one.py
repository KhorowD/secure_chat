from tkinter.constants import X
import gmpy2
from bitarray import *


A = 0x67452301
B = 0xEFCDAB89
C = 0x98BADCFE
D = 0x10325476
E = 0xC3D2E1F0

K = {1: 0x5A827999, 2: 0x6ED9EBA1, 3: 0x8F1BBCDC, 4: 0xCA62C1D6}

def to_binary(string: str):
    bin_array = bitarray()

    bin_array.frombytes(string.encode("utf-8"))

    return bin_array

def bin_xor(a: bitarray, b: bitarray, word_lenght=32):
    """
    Возвращает xor двух бинарных строк
    """
    # return bin(int(a,2)^int(b,2))[2:].zfill(word_lenght)
    return a^b

def bin_and(a: bitarray, b: bitarray, word_lenght=32):
    """
    Возвращает and двух бинарных строк
    """
    # return bin(int(a,2)&int(b,2))[2:].zfill(word_lenght)
    print(len(a))
    print(len(b))
    return a & b

def bin_or(a: bitarray, b: bitarray, word_lenght=32):
    """
    Возвращает or двух бинарных строк
    """
    # return bin(int(a,2)|int(b,2))[2:].zfill(word_lenght)
    return a | b

def bin_not(a: bitarray, word_lenght=32):
    """
    Возвращает or двух бинарных строк
    """
    # return bin(~int(a,2))[2:].zfill(word_lenght)
    return ~a

def func_1(b, c, d):
    """
    Функция для иттераций (0, 19)
    """
    return bin_or(bin_and(b,c),bin_and(bin_not(b),d))

def func_2(b, c, d):
    """
    Функция для иттераций (20, 39)
    """
    return bin_xor(bin_xor(b,c),d)

def func_3(b, c, d):
    """
    Функция для иттераций (40, 59)
    """
    return bin_or(bin_or(bin_and(b,c), bin_and(b,d)),bin_and(c, d))

def func_4(b, c, d):
    """
    Функция для иттераций (60, 79)
    """
    return bin_xor(bin_xor(b,c),d)

def add_padding(data: str):
    """
    Функция заполнения паддинга
    на вход поступает строка битов, которую необходимо дополнить
    до необходимо числа бит в зависимости от длины
    """
    lenght = len(data) # получаем длину данных

    print(f"number of bits = {lenght}")
    # padd_add_counter = 0

    mod_lenght = (lenght % 512)

    print(f"mod lenght = {mod_lenght}")

    if mod_lenght > 447 and mod_lenght < 512:
        new_data = data + "1"
        while len(new_data) < 512:
            new_data += "0"

        new_data = new_data + "0"*448
        # new_data = new_data + bitarray(lenght, endian='big')#lenght.to_bytes(64, 'big')
        print(type(new_data))
        new_data.extend(bitarray(lenght.to_bytes(64, byteorder='big')))
    elif mod_lenght < 448:
        new_data = data + "1"

        while len(new_data) < 448:
            new_data += "0"

        # new_data = new_data + bitarray(lenght, endian='big') #lenght.to_bytes(64, 'big')
        print(type(new_data))
        print(bitarray(lenght, endian='big'))
        new_data.extend(bitarray(lenght.to_bytes(64, byteorder='big')))
    else:
        new_data = data
        print(type(new_data))

    if len(new_data) % 512 == 0:
        print("padding added")

    return new_data


def sha_one_process(message: str):

    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    binary_data = to_binary(message)

    binary_data_with_padding = add_padding(binary_data)

    chunks = [binary_data_with_padding[x:x+512] for x in range(0, len(binary_data_with_padding), 512)]

    print(f"chunks is \n {chunks}")

    for chunk in chunks:
        print(f"chunk lengh = {len(chunk)}")
        words = [chunk[x:x+32] for x in range(0, len(chunk), 32)]

        print(f"words is \n {words}")

        for i in range(16, 80):
            # new_word = words[i-3] ^ words[i-8] ^ words[i-14] ^ words[i-16]
            new_word = bin_xor(bin_xor(bin_xor(words[i-2], words[i-7]), words[i-13]), words[i-15])
            words.append(new_word[:1] + new_word[1:]) # ROL


        # Инициация вектора
        a = bitarray(bin(h0)[2:])
        b = bitarray(bin(h1)[2:])
        c = bitarray(bin(h2)[2:])
        d = bitarray(bin(h3)[2:])
        e = bitarray(bin(h4)[2:])

        for i in range(0, 80):
            if i <= 19:
                f = func_1(b, c, d)
                k = K[1]
            elif 20 <= i and i <= 39:
                f = func_2(b, c, d)
                k = K[2]
            elif 40 <= i and i <= 59:
                f = func_3(b, c, d)
                k = K[3]
            elif 60 <= i and i <= 79:
                f = func_4(b, c, d)
                k = K[4]

            temp  = hex(int(a[:5] + a[5:], 2) + int(f, 2) + int(e, 2) + int(k, 2) + int(words[i], 2))
            e = hex(int(d,2))
            d = hex(int(c,2))
            c = hex(int(b[:30] + b[30:],2))
            b = hex(int(a,2))
            a = temp 

        h0 = h0 + ba2hex(a)#hex(int(a, 2))
        h1 = h1 + hex(int(b, 2))
        h2 = h2 + hex(int(c, 2))
        h3 = h3 + hex(int(d, 2))
        h4 = h4 + hex(int(e, 2))


    result = str(h0)[2:] + str(h1)[2:] + str(h2)[2:] + str(h3)[2:] + str(h4)[2:]

    if len(result) == 40:
        print("That's right")

    else:
        print("Smth wrong")

    return result

def main():

    message = input("enter some string\n")

    print(x := to_binary(message))

    print(add_padding(x))

    print(f"hash value = {sha_one_process(message)}")

if __name__ == "__main__":
    main()