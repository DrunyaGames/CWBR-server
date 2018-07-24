import struct
import binascii
import random


def random_hex():
    a, b, c = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    return '#' + binascii.hexlify(struct.pack('BBB', a, b, c)).decode()
