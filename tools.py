import struct
import binascii
import random


def random_hex():
    return '#' + binascii.hexlify(struct.pack('BBB', random.randint(0, 255),
                                              random.randint(0, 255),
                                              random.randint(0, 255))).decode()
