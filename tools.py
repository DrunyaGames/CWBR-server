import struct
import binascii
import random


def random_hex():
    while True:
        a, b, c = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        if a > 100 or b > 100 or c > 100:
            break
    return '#' + binascii.hexlify(struct.pack('BBB', a, b, c)).decode()
