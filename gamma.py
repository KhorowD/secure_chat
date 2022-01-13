"""Gamma encryption implementation by Khorov D.V. """

import secrets
import string
import random

binary = ""
encoded_binary = ""

def text_to_bits(text, encoding='utf-16', errors='surrogatepass'):
    """
        Функция переводит символы UTF-16 кодировки в строку бит
    """
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))


# def text_to_bits(text : bytes):
#     """
#         Функция переводит символы UTF-16 кодировки в строку бит
#     """
#     bits = bin(int.from_bytes(text, 'big'))[2:]
#     return bits.zfill(8 * ((len(bits) + 7) // 8))


def text_from_bits(bits, encoding='utf-16', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes(
        (n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'


# def text_from_bits(bits : bytes):
#     n = int(bits, 2)
#     return n.to_bytes(
#         (n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'


def gen_key(lenght):
    # alph = string.ascii_letters + string.digits
    # rand_str = "".join(secrets.choice(alph) for i in range(lenght))
    # return rand_str

    # 2^35 - repeat
    a = 84589
    c = 45989
    m = 217728

    X = random.randint(0, m - 1)

    result_gamma = str(X)
    result_gamma = text_to_bits(result_gamma)

    X_i = X

    while len(result_gamma) < lenght:
        X_i = (a * X_i + c) % m
        # print(X_i)
        result_gamma += text_to_bits(str(X_i))
        # print(result_gamma)

    if len(result_gamma) > lenght:
        result_gamma = result_gamma[:lenght]

    # print(result_gamma)

    return result_gamma


def gamma_encode_decode_(input_text, entered_key, mode):

    if mode == "file":
        # print(type(input_text))
        # print(type(int(entered_key,2).to_bytes(len(entered_key), 'big')))
        max_len = len(input_text)
        entered_key = int(entered_key, 2).to_bytes(len(entered_key), 'big')
        # encoded_bits = int(input_text[2:], 2) ^ int(entered_key[2:], 2)
        encoded_bits = int.from_bytes(input_text, "big") ^ int.from_bytes(
            entered_key, "big")
        # print(type(encoded_bits.to_bytes()))
        return encoded_bits.to_bytes(max_len, "big")

    bits_text = text_to_bits(input_text)
    print(bits_text)
    bits_key = text_to_bits(entered_key)
    print(bits_key)
    encoded_bits = int(bits_text, 2) ^ int(bits_key, 2)
    print(encoded_bits)
    output_text = text_from_bits(bin(encoded_bits)[2:])
    print(output_text)
    return output_text


def open_file(file_name):
    file = open(file_name, "rb")
    binary_data = file.read()
    print(binary_data)
    file.close()

    return binary_data


def write_file(binary_data, file_name):
    file = open(file_name, "wb")
    print(binary_data)
    file.write(binary_data)

    file.close()


def main():

    # text_en = "danil \n 123 приветВАZZ"
    # key = gen_key(len(text_en))
    # print(len(key))
    # text = vernam_encode_decode_(text_en, key)
    # result = vernam_encode_decode_(text, key)

    # a = b'123'
    # b = b'456'
    # print(a+b)
    mode = "file"

    text_en = open_file(
        "./gamma_test.pdf")  #.decode("cp1251", errors='surrogatepass')
    print(type(text_en))
    key = gen_key(len(text_en))
    print("generated key: ", key[:100])
    print(len(key))
    write_file(int(key, 2).to_bytes(len(key), 'big'), "example.key")
    text = gamma_encode_decode_(text_en, key, mode)
    write_file(text, "encoded.change")
    result = gamma_encode_decode_(
        text, key, mode)  #.encode("cp1251", errors='surrogatepass')[2:]
    print(result)
    write_file(result, "output.change")


if __name__ == '__main__':
    main()