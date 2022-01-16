# import primegen
from cmath import e
import re
import time
import secrets
from random import randint, SystemRandom
from primroot import primroot
from base_func import prime_gen_rm, RM_test, custom_pow
from gmpy2 import mpz, is_strong_prp


# Вычисляем параметры базовые p,q,g


def calc_parametrs(len_bits, flag="prim_root"):

    start_time = time.time()

    if flag == "prim_root":
        p = int(prime_gen_rm(len_bits), 2)
        q = 1 #заглушка
        g = primroot(p)

    else: 
        isNotPrime = True
        g = [2, 3, 4, 5, 6, 7]

        print("choose q, p")
        while isNotPrime:
            # p = int(prime_gen_rm(len_bits),
            #         2)  # генерируем число нужного числа бит и переводим в инт
            q = mpz(int(prime_gen_rm(len_bits),
                    2))  # генерируем число нужного числа бит и переводим в инт
            # q = p // 2  # Предпологаем что q большое простое число
            p = mpz(2*q + 1)
            if RM_test(bin(p)[2:]): # Проверяем q на простоту
                if p % q == 1:  # В случае, если оно большое простое число порядка p/2
                    isNotPrime = False  # Устанавливаем флаг что оно простое

        print(f"q = {q}")
        print(f"p = {p}")

        isNotPrimeRoot = True
        while isNotPrimeRoot:

            g_ind = randint(0, 5)
            if pow(g[g_ind], q, p) != 1:
                isNotPrimeRoot = False
        print(f"g = {g[g_ind]}")

        g = g[g_ind]

    print(f"time (min) = {(time.time() - start_time)/60}")

    print()

    return g, q, p


# Вычисляем Приватный\Открытый ключ для абонента X_a, Y_a


def gen_key_pair(p, g):
    
    abonent_secret = 1

    try:

        while abonent_secret == 1:
            abonent_secret = secrets.randbelow(
                p - 1)  # Генерируем с помощью безопасного генератора
            abonent_open = pow(g, abonent_secret, p)
    
    except Exception as e:
        print(e)

    return abonent_secret, abonent_open

#Процесс вычисления общего ключа

def get_secret(x, y, p):
    return custom_pow(y, x, p)

# Процесс шифрования побитовый

# Процесс расшифрования побитовый


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


# def dh_encode(msg_to_encode):

#     # переводим символы в числа
#     numbers_list = convert_chars_to_int(msg_to_encode)

#     print(numbers_list)

#     # генерируем простые числа
#     a_priv = primegen.prime_gen(40)
#     b_priv = primegen.prime_gen(40)

#     p = primegen.prime_gen(50)
#     q = primroot(p)

#     print(f"prime = {p}\n")

#     print(f"primitive root = {q}\n")

#     A_pub = pow(q, a_priv, p)
#     B_pub = pow(q, b_priv, p)

#     print(f"A_pub = {A_pub}, A_priv = {a_priv}\n")

#     print(f"B_pub = {B_pub}, A_priv = {b_priv}\n")

#     K_a = pow(B_pub, a_priv, p)
#     K_b = pow(A_pub, b_priv, p)

#     print(f"secret key = {K_a}\n")

#     print("Use cesar for encoding with sec. key\n")
#     encoded_num = [(num + K_a) % 255 for num in numbers_list]
#     print(encoded_num)

#     return convert_int_to_chars(encoded_num), K_a


# def dh_decode(msg_to_decode, key):
#     return convert_int_to_chars([(ord(ch) - key) % 255
#                                  for ch in msg_to_decode])


def main():

    start_time = time.time()

    # isLatinNumString = False

    # while isLatinNumString != True:

    #     # получаем входную строку
    #     message = input("Введите сообщение для отправки: ")

    #     if re.fullmatch("^[A-Za-z0-9]+$", message):
    #         isLatinNumString = True
    #     else:
    #         print("only Latin symbols and numbers")

    # encoded_message, sec_key = dh_encode(message)

    # print("Закодированное сообщение: " + encoded_message)

    # decoded_message = dh_decode(encoded_message, sec_key)

    # print("Декодированное сообщение: " + decoded_message)

    g, q, p = calc_parametrs(512, flag="a")

    print(g, q, p)

    x_a, y_a = gen_key_pair(p, g)

    print(f'secret = {x_a}, open_key = {y_a}')

    x_b, y_b = gen_key_pair(p, g)

    print(f'secret = {x_b}, open_key = {y_b}')

    Z_ab = get_secret(x_a, y_b, p)
    print(f"z_ab = {hex(Z_ab)}")

    Z_ba = get_secret(x_b, y_a, p)
    print(f"z_ba = {hex(Z_ba)}")


    print(f"time = {(time.time() - start_time)/60}")



if __name__ == '__main__':
    main()