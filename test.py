from sha_one import *
from help import *
from bitarray import bitarray, util

def test_chunks():

    a = codingsha(mes='hello')

    b = sha_one_process("hello")

    assert a == b