# from tkinter.constants import X
# import gmpy2
from bitarray import util, bitarray


A = 0x67452301
B = 0xEFCDAB89
C = 0x98BADCFE
D = 0x10325476
E = 0xC3D2E1F0

K = {1: 0x5A827999, 2: 0x6ED9EBA1, 3: 0x8F1BBCDC, 4: 0xCA62C1D6}

def to_binary(string: str):
    bin_array = bitarray(endian='big')

    bin_array.frombytes(string.encode())

    return bin_array

def insert_null(repeats, array):
    
    for r in range(0, repeats):
        array.insert(0, False)

    return array


def bin_xor(a, b, word_lenght=32):
    """
    Возвращает xor двух бинарных строк
    """
    if len(a) != word_lenght:
        insert_null(word_lenght - len(a), a)
    if len(b) != word_lenght:
        insert_null(word_lenght - len(b), b)
    # return bin(int(a,2)^int(b,2))[2:].zfill(word_lenght)
    return a^b

def bin_and(a, b, word_lenght=32):
    """
    Возвращает and двух бинарных строк
    """
    # return bin(int(a,2)&int(b,2))[2:].zfill(word_lenght)
    # print(len(a))
    # print(len(b))
    if len(a) < word_lenght:
        a = insert_null(word_lenght - len(a), a)
    if len(b) < word_lenght:
        b = insert_null(word_lenght - len(b), b)

    # print(f"len(a) = {len(a)}")
    # print(f"a = {a}")
    # print(f"len(b) = {len(b)}")
    # print(f"b = {b}")
    return a & b

def bin_or(a, b, word_lenght=32):
    """
    Возвращает or двух бинарных строк
    """
    # return bin(int(a,2)|int(b,2))[2:].zfill(word_lenght)
    # if len(a) != word_lenght:
    #     a = insert_null(word_lenght - len(a), a)
    # if len(b) != word_lenght:
    #     b = insert_null(word_lenght - len(b), b)
    return a | b

def bin_not(a, word_lenght=32):
    """
    Возвращает or двух бинарных строк
    """
    # return bin(~int(a,2))[2:].zfill(word_lenght)
    # if len(a) != word_lenght:
    #     a = insert_null(word_lenght - len(a), a)
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
    temp_1 = bin_and(b,c)
    temp_2 = bin_and(b,d)
    temp_3 = bin_and(c, d)

    result = bin_or(temp_1, temp_2)

    result = bin_or(result, temp_3)
    
    return result

def func_4(b, c, d):
    """
    Функция для иттераций (60, 79)
    """
    return bin_xor(bin_xor(b,c),d)

def ROL(word, pos):
    """
    Функция левого смещения
    Принимает массив битов и позицию смещения
    """

    if isinstance(word, bitarray) or isinstance(word, str):

        if len(word) < 32:
            word = insert_null(32-len(word), word)

        shifted = word[pos:] + word[:pos]

    elif isinstance(word, int):
        shifted = ((word << pos) | (word >> (32 - pos)))
    else:
        return None

    return shifted

def add_padding(chunks: list, msg_lenght: int):
    """
    Функция заполнения паддинга для Последнего блока (размером < 512)
    на вход поступает массив блоков
    """
    chunks_number = len(chunks) # получаем число блоков

    print(f"number of chunks = {chunks_number}")

    last_chunk = chunks_number - 1 # Определяем последний блок

    last_chunk_lenght = len(chunks[last_chunk])

    print(f"last chunk lenght = {last_chunk_lenght}")

    target_chunk = chunks[last_chunk]

    # Проверяем блок на выполнение условий

    if last_chunk_lenght < 448:
        new_chunk = target_chunk + "1"

        while len(new_chunk) < 448:
            new_chunk += "0"

        new_chunk.extend(util.int2ba(msg_lenght, 64, 'big'))

        chunks[last_chunk] = new_chunk

    elif last_chunk_lenght > 447 and last_chunk_lenght < 512:
        new_chunk = target_chunk + "1" 
        while len(new_chunk) < 512:
            new_chunk += "0"

        # Формируем второй блок
        new_chunk += "0"*448 

        # Добавляем длину исходного сообщения в формате 64 бит big-endian
        new_chunk.extend(util.int2ba(msg_lenght, 64, 'big'))
        
        # Добавляем блоки с падингом в массив блоков

        chunks[last_chunk] = new_chunk[:512]
        chunks.append(new_chunk[512:])
    
    if len(new_chunk) % 512 == 0:
        print("padding added")
    else:
        print("padding is not added correct!!!!!")

    return chunks

def convert_ba2int_array_test(array):
    integer_array = [util.ba2int(x) % pow(2, 32) for x in array]
    print(integer_array)

def convert_ba_2_int_array(array):
    return [util.ba2int(x) % pow(2, 32) for x in array]

def sha_one_process(message: str):

    h0 = 0x67452301
    h1 = 0xEFCDAB89
    h2 = 0x98BADCFE
    h3 = 0x10325476
    h4 = 0xC3D2E1F0
    
    binary_data = to_binary(message)

    chunks = [binary_data[x:x+512] for x in range(0, len(binary_data), 512)]

    print(f"Chunks before adding padding:\n{chunks}")

    chunks = add_padding(chunks, len(binary_data))

    print(f"Chunks after adding padding:\n{chunks}")
    
    for chunk in chunks:
        print(f"chunk lengh = {len(chunk)}")
        words = [chunk[x:x+32] for x in range(0, len(chunk), 32)]

        print(f"words is \n {words}")

        converted_words = convert_ba_2_int_array(words)

        print(f"converted words = {converted_words}")

        for i in range(16, 80):
            new_word = converted_words[i-3] ^  converted_words[i-8] ^ converted_words[i-14] ^ converted_words[i-16]
            new_word = new_word % pow(2, 32)
            new_word = ROL(new_word, 1)
            words.append(bitarray(bin(new_word)[2:]))
            converted_words.append(new_word)
            print(f"{i+1} word = {new_word} ")
            
        print(f"extended converted words = \n {converted_words}")

        print(f"extended words = {words}")

        # Инициация вектора
        a = bitarray(bin(h0)[2:])
        b = bitarray(bin(h1)[2:])
        c = bitarray(bin(h2)[2:])
        d = bitarray(bin(h3)[2:])
        d.insert(0, False)  #Добавляем незначимые нули для уравнивания массивов
        d.insert(0, False)
        d.insert(0, False)
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

            print(f"func result = {int(f.to01(), 2)}")
            print(f"A shift 5 = {util.ba2int(ROL(a, 5))}")
            temp_int = ( int(ROL(a.to01(), 5), 2) + int(f.to01(), 2) ) % pow(2, 32)
            print(f"temp_int = {temp_int}")
            temp_int = (temp_int + int(e.to01(), 2)) % pow(2, 32)
            print(f"temp_int = {temp_int}")
            temp_int = (temp_int + k) % pow(2, 32)
            print(f"temp_int = {temp_int}")
            temp_int = (temp_int + int(words[i].to01(), 2)) % pow(2, 32)
            print(f"temp_int = {temp_int}")
            temp = bitarray(bin(temp_int)[2:])
            print("before")
            print(util.ba2int(e), util.ba2int(d), util.ba2int(c), util.ba2int(b), util.ba2int(a))

            e = d
            d = c
            c = bitarray(ROL(b, 30))
            b = a 
            a = temp 

            print("after")
            print(util.ba2int(e), util.ba2int(d), util.ba2int(c), util.ba2int(b), util.ba2int(a))

        h0 = (h0 + util.ba2int(a)) % pow(2,32)  
        h1 = (h1 + util.ba2int(b)) % pow(2,32)
        h2 = (h2 + util.ba2int(c)) % pow(2,32)
        h3 = (h3 + util.ba2int(d)) % pow(2,32)
        h4 = (h4 + util.ba2int(e)) % pow(2,32)
        

    hash_parts = [h0, h1, h2, h3, h4]

    print(f"hash_parts = {hash_parts}")

    result = ""

    for i in hash_parts:
        temp_hex = hex(i)[2:] 

        if len(temp_hex) < 8:
            for j in range(0, 8 - len(temp_hex)):
                temp_hex = "0" + temp_hex

        result += temp_hex

    if len(result) == 40:
        print("That's right")
        print(result)
        print(len(result))

    else:
        print("Smth wrong")
        print(result)
        print(len(result))
    return result

def main():

    message = input("enter some string\n")
    print(f"hash value = {sha_one_process(message)}")

if __name__ == "__main__":
    main()