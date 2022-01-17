import re
from random import randint
from math import gcd, log2
import numpy as np
from io import IOBase
from base_func import custom_pow

# saved_data = None

def convert_chars_to_int(msg):
    """
    Функция перевода символов в числа
    """
    return [ord(ch) for ch in msg]


def convert_int_to_chars(num_to_decode):
    """
    Функция перевода чисел в символы
    """
    return "".join([chr(num) for num in num_to_decode])


def ext_gcd(a, b):
    """
    Реализация расширенного алгоритма Евклида
    Returns integer x:
        ax + by = gcd(a, b).
    """
    x, xx, y, yy = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x, xx = xx, x - xx * q
        y, yy = yy, y - yy * q
    return x


def gen_keys(p_prime,q_prime):
    """
    Функция, которая генерирует ключ абонента 
    """
    print(p_prime, q_prime)

    N = p_prime * q_prime

    phi = (p_prime - 1) * (q_prime - 1)

    e = randint(1,N)
    while gcd(e,phi) != 1:
        e = randint(1,N)
    
    # Обход варианта атаки с равным d и e
    # Таким образом мы гарантируем, что d и e разные
    d = e #Здесь приравниваем только для входа в алгоритм
    while d == e:
        d = ext_gcd(e, phi)

        if d < 0:
            d = d % phi

        print((e * d) % phi)

    return e, d, N, phi

def prepare_data(data):
    """
    Подготовка данных - деления на блоки по 8 байт (64 бита)
    Если блок не кратен 8, то добавляем ничего не значащие 0
    и последний байт паддинга  - это число добавленных байт.
    (См. ANSI x.923)
    data = np.ndarray(uint8)
    """

    # print(type(data))
    if isinstance(data, list) == False:
        data = data.tolist()

    # print(len(data))
    # print("Padd symbols number: ", len(data) % 8)

    if len(data) % 8 > 0:
        padding_counter = 8 - (len(data) % 8)
        for i in range(padding_counter - 1):
            data.append(0)
        data.append(padding_counter)

    return data

def delete_padding(data):

    last_byte = data[len(data) - 1]
    # print("     last_byte:", last_byte)
    if last_byte in [1, 2, 3, 4, 5, 6, 7]:
        null_bytes = data[len(data) - last_byte:len(data) - 1]
        # print(null_bytes)
        pattern = [0 for x in range(last_byte - 1)]
        # print(pattern)
        if null_bytes == pattern:
            return data[:len(data) - last_byte]

    return data

def convert_bytes_to_int():
    pass

def prepare_data(data, N):
    
    # print("----")
    # print(data)
    # print("----")
    # print(N)
    # print("====")
    #Длина ключа 
    n_lenght =  int(N,16).bit_length()
    # print("key_len = "+str(n_lenght))
    # предпологаемая длина блока (Уменьшаем на 1-цу для того, чтобы блок был точно < N)
    block_lenght = n_lenght - 1
    # print("block len =" + str(block_lenght))
    #Длина всех данных 
    data_lenght = 8 * len(data)
    # print("data_bin_len ="+str(data_lenght))

    # Полное число блоков для шифрования, + последний блок
    full_iter_number, it = divmod(data_lenght,block_lenght)

    # print(full_iter_number, it, block_lenght)
    # print("====")

    # переводим в двоичный вид
    data = "".join([bin(x)[2:].zfill(8) for x in data])
    # делим по длине блока, и дополняем нулями по длине блока (!!!!)
    data = [data[x:x+block_lenght].zfill(block_lenght) for x in range(0, len(data), block_lenght)]
    
    # data = [data[x:x+8] for x in range(0, len(data), 8)]
    # print(data)
    # print("+")

    return data, block_lenght


def fast_pow(number, e, N):
    # print("power " + e)
    # print(int(e, 16))
    # print("mod " + N)
    # print(int(N,16))
    # print("number to encode " + number)
    # print(int(bin_number, 2))
    # Changed  int(bin_number, 2) to int bin_number
    result = custom_pow(int(number), int(e[2:], 16), int(N[2:],16))
    # print(result)
    return result


def encode(data, e_exp, N):
    # Делим данные на блоки

    # data, block_lenght  = prepare_data(data, N)
    # print("data to encode")
    # for i in data:
    #     print(i)
    #     print(type(i))
    # print("+")
    
    # в цикле с помощью fast POW шифруем
    
    # encoded_data = [bin(fast_pow(data_part, e_exp, N))[2:].zfill(block_lenght) for data_part in data]
    # encoded_data = [bin(fast_pow(data_part, e_exp, N))[2:] for data_part in data]
    encoded_data = [hex(fast_pow(data_part, e_exp, N))[2:] for data_part in data]

    # print("finaly hex encoded data")
    # print(encoded_data)
    # переводим назад в байты

    # encoded_data = hex(int("".join(encoded_data), 2))
    # print(encoded_data)
    
    # возвращаем информацию
    return encoded_data
    
def de_prepare_data(data, N):
    # Определяем длину блока
    block_lenght = int(N,16).bit_length() - 1
    # переводим в двоичный вид
    # data = "".join([bin(x)[2:].zfill(8) for x in data])
    if "\n" in data:
        data = data.split("\n")
    else:
        data = [data]

    # print(data)

    if data[-1] == "":
        del data[-1]
    # print(data)
    # Делим по длине блока
    # data = [data[x:x+block_lenght] for x in range(0, len(data), block_lenght)]
    # data = [data[x:x+8] for x in range(0, len(data), 8)]
    # data = [bin(int(x,16))[2:].zfill(block_lenght) for x in data]
    data = [str(int(x,16)) for x in data]
    # print("+")

    return data

def decode(data, d_exp, N):

    # Делим данные на блоки

    data  = de_prepare_data(data, N)
    # print("de_prepared data")
    # print(data)
    # в цикле с помощью fast POW шифруем
    
    decoded_data = [fast_pow(data_part, d_exp, N) for data_part in data]

    # print("finaly decoded data")
    # print(decoded_data)
    # переводим назад в байты

    # decoded_data = 
    # decoded_data = "".join(decoded_data)

    # decoded_data = [decoded_data[x:x+8] for x in range(0 , len(decoded_data), 8)]
    
    # print(decoded_data)

    # decoded_data = np.array(decoded_data, dtype="uint8").tobytes().decode()
    # возвращаем информацию
    return decoded_data

def rsa_encode(msg_to_encode):

    # переводим символы в числа
    numbers_list = convert_chars_to_int(msg_to_encode)

    print(numbers_list)

    C_a, D_a, N_a = gen_keys(50)
    C_b, D_b, N_b = gen_keys(50)

    print(f"A keys c_a = {C_a},  d_a = {D_a}, N_a = {N_a}\n")
    print(f"B keys c_b = {C_b},  d_b = {D_b}, N_b = {N_b}\n")

    A_sig = [pow(num, C_a, N_a) for num in numbers_list]

    print("Sign")

    print(A_sig)

    encoded_list = [pow(num, D_b, N_b) for num in A_sig]
    print("Encoded")
    print(encoded_list)

    return encoded_list, C_b, D_a, N_a, N_b


def rsa_decode(msg_to_decode, key_b, pub_key_a, N_a, N_b):

    A_sig = [pow(num, key_b, N_b) for num in msg_to_decode]
    print("Sign")
    print(A_sig)
    return convert_int_to_chars([pow(num, pub_key_a, N_a) for num in A_sig])

def read_from_file(path, mode="text", proc="encode"):
    """
    Чтение файла в виде текста или бинарном формате
    mode -> text or bin
    """

    if mode == "text":
        file = open(path, "r")
    if mode == "bin":
        if proc=="decode":
            # file = np.genfromtxt(path, dtype="str")
            file = open(path, "r")
        else:
            file = open(path, "rb")

    return file

def save_to_file(data, fname, mode="text", proc="encode"):
    """
    Сохраняем байты в виде текста или бинарном формате
    mode -> text or bin
    proc -> encode or decode
    """
    if mode == "text":
        np.savetxt(fname, data, newline="", fmt="%c")
    if mode == "bin":
        if proc == "encode":
            
            np.savetxt(fname, data, newline="\n", fmt="%s")
        else:
            np.array(data, dtype="uint8").tofile(fname)

def to_bytes(input_data):
    """
    Переводим строку или файл в байты, на выходе список содержащий значения байт
    input_data = str OR file type (checked here)
    """

    if isinstance(input_data, str):
        print("to_bytes: convert str")
        input_bytes = np.frombuffer(input_data.encode(), dtype="uint8")
        # print(len(input_bytes))
    elif isinstance(input_data, IOBase):
        print("to_bytes: convert file")
        input_bytes = np.fromfile(input_data, dtype="uint8")
    elif isinstance(input_data, bytes):
        print("to_bytes: convert bytes")
        input_bytes = np.frombuffer(input_data, dtype="uint8")
    else:
        return None

    return input_bytes

def main():

    isLatinNumString = False

    while isLatinNumString != True:

        # получаем входную строку
        message = input("Введите сообщение для отправки: ")

        if re.fullmatch("^[A-Za-z0-9]+$", message):
            isLatinNumString = True
        else:
            print("only Latin symbols and numbers")

    encoded_message, sec_key_b, open_key_a, N_a, N_b = rsa_encode(message)

    decoded_message = rsa_decode(
        encoded_message, sec_key_b, open_key_a, N_a, N_b)

    print("Декодированное сообщение: " + decoded_message)


if __name__ == '__main__':
    main()