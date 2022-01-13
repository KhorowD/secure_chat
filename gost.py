""" GOST implementation by Khorov D.V."""

import secrets
import string
import time

import numpy as np
from io import IOBase

GOST_SBOXES = [[1, 11, 12, 2, 9, 13, 0, 15, 4, 5, 8, 14, 10, 7, 6, 3],
               [0, 1, 7, 13, 11, 4, 5, 2, 8, 14, 15, 12, 9, 10, 6, 3],
               [8, 2, 5, 0, 4, 9, 15, 10, 3, 7, 12, 13, 6, 14, 1, 11],
               [3, 6, 0, 1, 5, 13, 10, 8, 11, 2, 9, 7, 14, 15, 12, 4],
               [8, 13, 11, 0, 4, 5, 1, 2, 9, 3, 12, 14, 6, 15, 10, 7],
               [12, 9, 11, 1, 8, 14, 2, 4, 7, 3, 6, 5, 10, 0, 15, 13],
               [10, 9, 6, 8, 13, 14, 2, 0, 15, 3, 5, 11, 4, 1, 12, 7],
               [7, 4, 0, 5, 10, 2, 15, 14, 12, 6, 1, 11, 13, 9, 3, 8]]

GOST_DATA = ""
GOST_FILE = ""


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


def permutation(data, pattern):
    """
    Перестановка входных данных по заранее заданому шаблону
    data = str 
    pattern = list(int)
    """
    result = ""
    for ind in pattern:
        result += data[ind - 1]

    return result


def save_to_file(data, fname, mode="text"):
    """
    Сохраняем байты в виде текста или бинарном формате
    mode -> text or bin
    """
    if mode == "text":
        np.savetxt(fname, data, newline="", fmt="%c")
    if mode == "bin":
        np.array(data, dtype="uint8").tofile(fname)


def read_from_file(path, mode="text"):
    """
    Чтение файла в виде текста или бинарном формате
    mode -> text or bin
    """

    if mode == "text":
        file = open(path, "r")
    if mode == "bin":
        file = open(path, "rb")

    return file


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


def gen_round_key(key):
    """
    Генерирование раундовых ключей, по заданому первичному ключу
    key = str - > 32 chars ASCII
    """
    # переводим в байты
    bytes_key = to_bytes(key)

    # переводим в строку бит
    bits_key = "".join([bin(x)[2:].zfill(8) for x in bytes_key])

    # возвращаем 8 ключей в прямом порядке
    return [bits_key[x:x + 32] for x in range(0, len(bits_key), 32)]


def gen_init_key():
    """
    Генерирование первичного ключа
    """

    # Ascii символы и числа
    alph = string.ascii_letters + string.digits
    rand_str = "".join(secrets.choice(alph) for i in range(32))
    return rand_str


def xor(block, key):
    """
    Функция сложения по модулю 2 блока с раундовым ключем
    block = int -> number
    key = str -> 48 bits
    """
    div_key = [key[x:x + 8] for x in range(0, len(key), 8)]

    xor_bytes = []
    for b, k in zip(block, div_key):
        xor_bytes.append(b ^ int(k, 2))

    return xor_bytes


def delete_padding(data):

    last_byte = data[len(data) - 1]
    print("     last_byte:", last_byte)
    if last_byte in [1, 2, 3, 4, 5, 6, 7]:
        null_bytes = data[len(data) - last_byte:len(data) - 1]
        print(null_bytes)
        pattern = [0 for x in range(last_byte - 1)]
        print(pattern)
        if null_bytes == pattern:
            return data[:len(data) - last_byte]

    return data


def s_block_value(block_4_bits, s_block_ind):
    """
    Функция, которая применяет блок подстановок
    block_4_bits = str - 4bits
    s_block_ind = number of s-block [0-7]
    """
    return bin(GOST_SBOXES[s_block_ind][int(block_4_bits, 2)])[2:].zfill(4)


def f_function(sub_block, round_key):
    """
    Функция (Фейстеля) F - отвечает за раундовое преобразование  половины 
    блока
    sub_block = list(int) -> 4 bytes -> 32 bits
    round_key = str -> 32 bits 
    """
    # переводим блок в двоичный вид
    block_bits = "".join([bin(x)[2:].zfill(8) for x in sub_block])

    # Складываем по модулю 2^32 блок и ключ

    block = bin(
        (int(block_bits, 2) + int(round_key, 2)) % pow(2, 32))[2:].zfill(32)

    # Делим блок на 8 4-х битовых блока

    blocks_4bits = [block[x:x + 4] for x in range(0, len(block), 4)]

    # преобразуем через s-блоки

    blocks_4bits = "".join([
        s_block_value(blocks_4bits[i], i) for i in range(0, len(blocks_4bits))
    ])

    # делаем циклический сдвиг на 11 бит влево

    result_block = blocks_4bits[:11] + blocks_4bits[11:]

    return [
        int(result_block[x:x + 8], 2) for x in range(0, len(result_block), 8)
    ]


def round_ECB(left_part, right_part, cur_key):
    """
    Функция одного раунда шифрования/расшифрования
    left_part = list(int) - > 4 bytes
    right_part = list(int) - > 4 bytes
    cur_key = str -> 32 bits
    """

    # Преобразуем один блок через функцию Фейстеля
    after_f_block = f_function(right_part, cur_key)

    # Формируем новый блок из блока на выходе ф-ции Фейстеля
    new_right_block = [x1 ^ x2 for x1, x2 in zip(left_part, after_f_block)]

    # Меняем положение второго блока
    new_left_block = right_part

    return new_left_block, new_right_block


def mode_ECB(data, keys, progress_bar, reverse=False):

    # преобразуем данные в байты
    input_bytes = to_bytes(data)

    # Добавляем паддинг
    prepared_data = prepare_data(input_bytes)
    print("Data with padd: ", prepared_data)

    # Разделяем данные на порции по 8 байт (64 бита)
    blocks_64 = [
        prepared_data[x:x + 8] for x in range(0, len(prepared_data), 8)
    ]

    encoded_blocks = []

    bar_curr_value = 0.0

    progress_bar.setValue(bar_curr_value)

    bar_step_value = 100 / len(blocks_64)

    # Для каждого блока проводим шифрование
    for block in blocks_64:

        # Делим блок на две части по 4 байта (32 бита)
        left = block[:4]
        right = block[4:]

        if reverse == False:
            # Выполняем 24 раунда шифрования с ключами в прямом порядке
            for i in range(24):
                # print(i % 8)
                left, right = round_ECB(left, right, keys[i % 8])

            # Высолняем 8 раундов шифрования с ключами в обратном порядке
            for i in range(8):
                # print(7-i)
                left, right = round_ECB(left, right, keys[7 - i])

        else:
            # Высолняем 8 раундов шифрования с ключами в обратном порядке
            for i in range(8):
                # print(i)
                left, right = round_ECB(left, right, keys[i])

            # Выполняем 24 раунда шифрования с ключами в прямом порядке
            for i in range(24):
                # print((23 - i)%8)
                left, right = round_ECB(left, right, keys[(23 - i) % 8])

        # result_block = left + right
        result_block = right + left
        # if reverse == True:
        #     result_block = right + left
        # else:
        #     result_block = left + right

        # Объединяем блоки вместе, и сохраняем в отдельный массив
        encoded_blocks.extend(result_block)

        # Работа с progress bar
        bar_curr_value += bar_step_value
        progress_bar.setValue(bar_curr_value)

    if reverse == True:
        encoded_blocks = delete_padding(encoded_blocks)

    return encoded_blocks


def mode_OFB(data, keys, init_vect, progress_bar, reverse=False):
    # преобразуем данные в байты
    input_bytes = to_bytes(data)

    # Добавляем паддинг
    prepared_data = prepare_data(input_bytes)

    # Преобразуем IV к байтам
    curr_vect = [
        int(init_vect[x:x + 8], 2) for x in range(0, len(init_vect), 8)
    ]
    print(curr_vect)

    # Разделяем данные на порции по 8 байт (64 бита)
    blocks_64 = [
        prepared_data[x:x + 8] for x in range(0, len(prepared_data), 8)
    ]

    #print(blocks_64)

    encoded_blocks = []

    bar_curr_value = 0.0

    progress_bar.setValue(bar_curr_value)

    bar_step_value = 100 / len(blocks_64)

    # Для каждого блока проводим шифрование
    for block in blocks_64:

        # Делим блок на две части по 4 байта (32 бита)
        left = curr_vect[:4]
        right = curr_vect[4:]

        # Выполняем 24 раунда шифрования с ключами в прямом порядке
        for i in range(24):
            left, right = round_ECB(left, right, keys[i % 8])

        # Высолняем 8 раундов шифрования с ключами в обратном порядке
        for i in range(8):
            left, right = round_ECB(left, right, keys[7 - i])

        # result_block = left + right
        result_block = right + left
        len(result_block)
        len(block)

        # Сложение IV блока полсе DES c текущим блоком
        int_result_block = [x1 ^ x2 for x1, x2 in zip(result_block, block)]

        # изменяем текущий блок для сцепления
        # curr_vect = int_result_block
        if reverse == True:
            curr_vect = block
        else:
            curr_vect = int_result_block
        #print("next curr vect", curr_vect)

        #print("cyphered block: ", int_result_block)

        # Объединяем блоки вместе, и сохраняем в отдельный массив
        encoded_blocks.extend(int_result_block)

        # Работа с progress bar
        bar_curr_value += bar_step_value
        progress_bar.setValue(bar_curr_value)

    if reverse == True:
        encoded_blocks = delete_padding(encoded_blocks)

    return encoded_blocks


def encode(input_data, input_key, init_vect, mode, progress_bar):

    # Проверяем длину ключа и если она равна 32 то генерируем раундовые ключи
    if len(input_key) == 32:
        key_32 = gen_round_key(input_key)
    else:
        return None

    # В зависимости от режима шифрования, выбираем режим работы алгоритма
    if mode == 0:  #ECB

        encoded_data = mode_ECB(input_data, key_32, progress_bar)
        # print("Encoded data: ", encoded_data)
        return encoded_data

    else:  #OFB
        encoded_data = mode_OFB(input_data, key_32, init_vect, progress_bar)
        # print("Encoded data: ", encoded_data)
        return encoded_data


def decode(input_data, input_key, init_vect, mode, progress_bar):

    # Проверяем длину ключа и если она равна 7 то генерируем раундовые ключи
    if len(input_key) == 32:
        # Здесь вычисляем те же ключи и подаем их в обратном порядке
        key_32 = gen_round_key(input_key)
    else:
        return None

    # В зависимости от режима шифрования, выбираем режим работы алгоритма
    if mode == 0:  #ECB

        decoded_data = mode_ECB(input_data, key_32, progress_bar, reverse=True)
        # print("Decoded data: ", decoded_data)
        return decoded_data

    else:  #OFB
        decoded_data = mode_OFB(input_data,
                                key_32,
                                init_vect,
                                progress_bar,
                                reverse=True)
        # print("Decoded data: ", decoded_data)
        return decoded_data


def main():

    pass
    # path = "./des_examples/odbg201.zip"

    # file = read_from_file(path, mode="bin")

    # text = "Данил"

    # base_key = gen_init_key()

    # print(base_key, " - init key")

    # start_time = time.time()

    # encoded = encode(text, base_key, 0, 0, QtWidgets.QProgressBar())

    # print("Encode time: ", (time.time() - start_time) / 60)

    # save_to_file(encoded, mode="bin")

    # try:
    #     text = text.decode()
    # except UnicodeDecodeError:
    #     print("Decode Error! Use HEX view")

    # print("Encoded to text: ", text)
    # print(len(text))

    # # text = open("./des_examples/encoded.des", "rb")
    # # file = read_from_file("./des_examples/test.des", mode="bin")

    # start_time = time.time()

    # decoded = decode(text, base_key, 0, 0, QtWidgets.QProgressBar())

    # print("Decode time: ", (time.time() - start_time) / 60)
    # # print(type(decoded))
    # text = np.array(decoded, dtype="uint8").tobytes().decode()
    # # text = np.array(encoded, dtype="uint8").tofile("./des_test1.txt")
    # # np.savetxt("./des_test1.txt", decoded, newline="",fmt="%c")
    # # save_to_file(decoded, mode="bin")
    # print(text)

    # print("Fin")


if __name__ == "__main__":
    main()