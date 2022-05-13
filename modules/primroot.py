from .pyecm import factors
from gmpy2 import is_prime, f_div, mpz, mpfr, is_odd


def primroot(n):
    s = set()
    # находим функцию эйлера
    phi = mpz(n - 1)

    # факторизуем функцию эйлера
    s = set(factors(phi, False, True, 10, 1))
    for r in range(2, phi + 1):
        # Проходимся по всем простым делителям phi
        # и проверяем, если найдена степень равная 1
        flag = False
        for it in s:

            # Проверяем если r^((phi)/primefactors)
            # mod n сравнимо с 1 или нет
            if (pow(r, phi // it, n) == 1):
                flag = True
                break
        # если найден первообразный корень
        if (flag == False):
            return r

            # если не найдено первообразного корня
    return -1
