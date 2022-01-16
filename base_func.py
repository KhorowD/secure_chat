import time
from sympy import prime
from random import randint, random, getrandbits
from gmpy2 import is_prime, f_div, mpz, mpfr, is_odd, is_strong_prp

FIRST_2000_PRIME = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409, 419,
    421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499, 503,
    509, 521, 523, 541, 547, 557, 563, 569, 571, 577, 587, 593, 599, 601, 607,
    613, 617, 619, 631, 641, 643, 647, 653, 659, 661, 673, 677, 683, 691, 701,
    709, 719, 727, 733, 739, 743, 751, 757, 761, 769, 773, 787, 797, 809, 811,
    821, 823, 827, 829, 839, 853, 857, 859, 863, 877, 881, 883, 887, 907, 911,
    919, 929, 937, 941, 947, 953, 967, 971, 977, 983, 991, 997, 1009, 1013,
    1019, 1021, 1031, 1033, 1039, 1049, 1051, 1061, 1063, 1069, 1087, 1091,
    1093, 1097, 1103, 1109, 1117, 1123, 1129, 1151, 1153, 1163, 1171, 1181,
    1187, 1193, 1201, 1213, 1217, 1223, 1229, 1231, 1237, 1249, 1259, 1277,
    1279, 1283, 1289, 1291, 1297, 1301, 1303, 1307, 1319, 1321, 1327, 1361,
    1367, 1373, 1381, 1399, 1409, 1423, 1427, 1429, 1433, 1439, 1447, 1451,
    1453, 1459, 1471, 1481, 1483, 1487, 1489, 1493, 1499, 1511, 1523, 1531,
    1543, 1549, 1553, 1559, 1567, 1571, 1579, 1583, 1597, 1601, 1607, 1609,
    1613, 1619, 1621, 1627, 1637, 1657, 1663, 1667, 1669, 1693, 1697, 1699,
    1709, 1721, 1723, 1733, 1741, 1747, 1753, 1759, 1777, 1783, 1787, 1789,
    1801, 1811, 1823, 1831, 1847, 1861, 1867, 1871, 1873, 1877, 1879, 1889,
    1901, 1907, 1913, 1931, 1933, 1949, 1951, 1973, 1979, 1987, 1993, 1997,
    1999
]


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
    return x, y


# def custom_pow(a :int, x :int, p :int):
#     """
#     Реализация алгоритма возведения в степень
#     х - Степень 
#     p - модуль
#     а - число возводимое в степень

#     returns - a^x mod p 
#     """

#     # Представление числа х в двоичном виде

#     x_binary = bin(x)[2:]
#     # print("bin view exp: " + x_binary)

#     # инициализируем входные параметры
#     result = 1
#     s = a

#     for i in range(0, len(x_binary)):
#         if x_binary[(len(x_binary) - 1) - i] == '1':
#             result = (result * s) % p
#         s = (s * s) % p

#     return result

def custom_pow(a :int, x :int, p :int):
    """
    Реализация алгоритма возведения в степень
    х - Степень 
    p - модуль
    а - число возводимое в степень

    returns - a^x mod p 
    """

    # Представление числа х в двоичном виде

    x_binary = bin(x)[2:]
    # print("bin view exp: " + x_binary)

    # инициализируем входные параметры
    result = mpz(1)
    s = mpz(a)

    for i in range(0, len(x_binary)):
        if x_binary[(len(x_binary) - 1) - i] == '1':
            result = (result * s) % p
        s = (s * s) % p

    return result

def prime_gen_dm(dimension):
    """
    Используем алгоритм Диемитко для генерации чисел нужного порядка
    """
    start_prime = chose_start_prime(dimension)

    current_prime = mpz(start_prime)

    p = mpz(start_prime)

    repit_flag = True

    U = 0

    while p.num_digits() <= dimension:
        if repit_flag:
            repit_flag = False
            N = f_div(mpz(10**(dimension - 1)), mpz(current_prime)) + \
                f_div(mpz(10**(dimension - 1) * mpfr(random())),
                      mpz(current_prime))
            N = N + 1 if N.is_odd() else N
            U = 0
        p = (N + U) * current_prime + 1
        if pow(2, p - 1, p) == 1 and pow(2, N + U, p) != 1:
            repit_flag = True
            break
        else:
            U += 2

    return p


"""
Функция для выбора простого числа небольшого порядка, для старта алгоритма Диемитко
"""


def chose_start_prime(position):
    return prime(position + randint(10, 100))


def choose_base_number(lenght):
    """
    Функция генерации стартового числа для проверки на простоту
    """
    # Формируем стартовое значение
    start_number = ""
    while (len(start_number) != lenght):
        start_number = format(
            getrandbits(lenght - 1) + (1 << lenght - 1),
            str(lenght) + 'b')

        start_number = "1" + start_number[
            1:len(start_number) -
            1] + "1"  #Выставляем первый и последний бит "1"

    return start_number

def test_div_first_2000(test_number):
    """
    Функция проверки делимости на первые простые числа < 2k
    """
    test_number = int(test_number, 2)
    for i in FIRST_2000_PRIME[:256]:  #здесь костыль только 256 чисел
        if (test_number % i) == 0:
            return True  #если тест не прошел

    return False  #если тест прошел


def RM_test(test_number):
    """
    Алгоритм тестирования Рабина-Миллера 
    """

    test_number = int(test_number, 2)
    if (test_number <= 3): return False  #Проверка на условие n>3

    # Проверка на делимость первых 256 простых чисел
    if test_div_first_2000(bin(test_number)[2:]): return False

    power = 0#mpz(0)
    remainder = 0#mpz(0)
    number_to_div_2 =test_number - 1 #mpz(test_number - 1)

    while (remainder % 2 == 0):
        number_to_div_2, remainder = divmod(number_to_div_2, 2)
        if remainder == 0:
            power += 1
        else:
            break
    
    odd_part = (test_number - 1) // 2**power

    for k in range(0, 5):
        a = randint(2, test_number - 2)

        if ((x := pow(a, odd_part, test_number)) == (1 or test_number - 1)):
            continue
        for i in range(1, power):
            x = pow(x, 2, test_number)
            if x == test_number - 1:
                break
        else:
            return False

    return True

# @jit(fastmath=True, parallel=True)
def RM_test_gmpy(test_number):
    """
    Вариант проверки простоты с помощью gmpy2
    """

    test_number = mpz(int(test_number, 2))

    return is_strong_prp(test_number, 2)


def prime_gen_rm(key_lenght):
    """
    Второй вариант функции генерации большого простого числа с использованием 
    Теста Рабина-Милера 
    """

    is_not_prime = True
    while (is_not_prime):
        # Формируем стартовое значение
        start_number = choose_base_number(key_lenght)

        if RM_test(start_number):
            return start_number
        else:
            is_not_prime = True


def main():

    # check pow
    # print(
    #     custom_pow(
    #         9029388504640441911464367553668152525044981194402670276994373411317742162769311729130148787981498006,
    #         13, 3))

    print(custom_pow(395229702, 128089133, 565513309))

    # check gcd

    # check inversion

    # check prime generator

    # print(prime_gen(100))

    # prime_gen_rm(1024)

    # print(RM_test(977))
    # start_time = time.time()
    # number = prime_gen_rm(1024)

    # print(int(number, 2))

    # print("check gen prime, exp time: " +
    #       str((time.time() - start_time) / 60) + " min")


if __name__ == "__main__":
    main()