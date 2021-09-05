""" This module focuses on conversions of string values, returning the converted value also as a
string.

This was designed as for custom command use in Splunk hence the str in str out rule.

__constants__:
    ACCEPTABLE_CONVERSIONS

__functions__:
    _parse_args
    _strip_binary
    _strip_hex
    baud_to_kbaud
    binary_to_decimal
    binary_to_hex
    bytestring_to_decimal
    decimal_to_binary
    decimal_to_hex
    decode_ascii_from_binary
    decode_ascii_from_hex
    encode_ascii_to_binary
    encode_ascii_to_decimal
    encode_ascii_to_hex
    hex_to_binary
    hex_to_decimal
    hhz_to_mhz
    hz_to_mhz
    kbaud_to_baud
    mhz_to_hz
    mhz_to_hhz


@author: dcsteve24
__python__version__ = 'Py2/Py3'
__os__ = All
__updated__ = '2021-09-05'
"""

import binascii
import codecs

from argparse import ArgumentParser


# A list of the conversion function present. For use as value checks.
ACCEPTABLE_STR_CONVERSIONS = [
    'baud_to_kbaud', 'binary_to_decimal', 'binary_to_hex', 'bytestring_to_decimal',
    'decimal_to_binary', 'decimal_to_hex', 'decode_ascii_from_binary', 'decode_ascii_from_hex',
    'encode_ascii_to_binary', 'encode_ascii_to_decimal', 'encode_ascii_to_hex', 'hex_to_binary',
    'hex_to_decimal', 'hhz_to_mhz', 'hz_to_mhz', 'kbaud_to_baud', 'mhz_to_hhz', 'mhz_to_hz']


def _parse_args():
    """ Uses ArgumentParser to parse in the passed arguments. """
    parser = ArgumentParser(description='Convert a string value and return the converted string'
                            ' value')
    parser.add_argument('conversion', choices=ACCEPTABLE_STR_CONVERSIONS, help='The conversion to'
                        ' perform')
    parser.add_argument('string_value', help='The original value to convert as a string')
    return parser.parse_args()


def _strip_binary(binary):
    """ Strips a binary value to just the binary itself; removing any spaces and the '0b' indicator.

    Args:
        binary: Str value containing the binary representation with or without the 0b and/or spaces
            in between the nibbles.

    Returns:
        The binary value back without spaces and the '0b' indicator.
    """
    return binary.split('b')[-1].replace(' ', '')


def _strip_hex(hex_value):
    """ Strips a hex value to just the hex itself; removing any spaces and the '0x' indicator.

    Args:
        hex_value: Str value containing the hex representation with or without the 0x and or/spaces.

    Returns:
        The hex value back withour spaces and the '0x' indicator.
    """
    return hex_value.split('x')[-1].replace(' ', '')


def baud_to_kbaud(bauds):
    """ Converts baud rate into kbaud rate

    Args:
        bauds: Str value containing baud (symbols per second)

    Return:
        Str value of the kbaud (kilo symbols per second)
    """
    return str(float(bauds) * 10 ** -3)


def binary_to_decimal(binary):
    """ Converts binary representation to decimal representation.

    Args:
        binary: Str value containing the binary representation with or without the 0b and/or spaces
            between the nibbles.

    Return:
        Str value of the decimal respresentation and without the 0b.
    """
    return str(int(_strip_binary(binary), 2))


def binary_to_hex(binary):
    """ Converts binary representation to hex representation.

    Args:
        binary: Str value containing the binary representation with or without the 0b and/or spaces
            in between the nibbles.

    Returns:
        Str value of hex representation and without the 0x.
    """
    stripped_binary = _strip_binary(binary)
    return '%0*X' % ((len(stripped_binary) + 3) // 4, int(stripped_binary, 2))


def bytestring_to_decimal(bytestring):
    """ Converts a bytestring into the ascii decimal representation (b'\xc0\x01' -> '49153')

    Args:
        bytestring: Byte String. Contains bytes in string format.

    Returns:
        Str value of the Byte String in decimal representation
    """
    return str(int(bytestring.encode('hex'), 16))


def decimal_to_binary(decimal):
    """ Converts decimal representation to binary representation.

    Args:
        decimal: Str value containing the decimal representation.

    Returns:
        Str value of the binary representation and without the 0b. Always returns 8 bits.
    """
    binary = _strip_binary(bin(int(decimal)))
    binary_len = len(binary)
    return binary if binary_len == 8 else '0'*(8-binary_len) + binary


def decimal_to_hex(decimal):
    """ Converts decimal representation to hex representation.

    Args:
        decimal: Str value containing the decimal representation

    Return:
        Str value of hex representation and without the 0x
    """
    return _strip_hex(hex(int(decimal)))


def decode_ascii_from_binary(binary):
    """ Decodes ascii from a binary representation of data ('1010' -> 'a').

    Args:
        binary: Str value containing the binary representation with or without the 0b and/or spaces
            in between the nibbles.

    Returns:
        Str vale containing the ascii of the binary representation passed. If a bad byte value is
        contained it will pass back a '0' value. So you may end up with something like 'Taco 0ell'.
    """
    # We use the custom module instead of passing directly to binascii so we still get values back
    # if crud is with the ascii. I'd rather get back 'Taco 0ell' and go from there than get back
    # nothing because of an error from one bad value.
    return decode_ascii_from_hex(binary_to_hex(binary))


def decode_ascii_from_hex(hex_value):
    """ Decodes ascii from a hex representation ('61' -> 'a').

    Args:
        hex_value: Str value containing the hex representation with or without the 0x and/or spaces

    Returns:
        Str value containing the ascii of the hex representation passed. If a bad hex value is
        contained it will pass back a '0' value. So you may end up with something like 'Taco 0ell'.
    """
    stripped_hex = _strip_hex(hex_value)
    hex_list = [stripped_hex[i:i+2] for i in range(0, len(stripped_hex), 2)]
    for i, grouping in enumerate(hex_list):
        try:
            hex_list[i] = str(codecs.decode(codecs.decode(grouping, 'hex'), 'ascii'))
        except UnicodeDecodeError:
            hex_list[i] - '0'
    return ''.join(hex_list)


def encode_ascii_to_binary(ascii_value):
    """Encodes a string value into the ascii binary representation ('a' -> '01100001')

    Args:
        ascii_value: Str value contiaining the value to convert.

    Returns:
        Str value of the ascii encoded binary representation.
    """
    return hex_to_binary(encode_ascii_to_binary(ascii_value))


def encode_ascii_to_decimal(ascii_value):
    """ Encodes a string value into the ascii decimal representation ('ab' -> '9798')

    Args:
        ascii_value: Str value containing the value to convert.

    Returns:
        Str value of the ascii encoded decimal representation.
    """
    return ''.join(format(ord(val), 'd') for val in ascii_value)


def encode_ascii_to_hex(ascii_value):
    """ Encodes a string value into the ascii hex representation ('a' -> '61')

    Args:
        ascii_value: Str value containing the value to convert.

    Returns:
        Str value of the ascii encoded hex representation.
    """
    return binascii.hexlify(ascii_value)


def hex_to_binary(hex_value):
    """ Converts the hex representation to binary representation.

    Args:
        hex_value: Str value containing the hex representation of a value with or without the 0x
        and/or spaces.

    Returns:
        Str value of the binary representation and without the 0b. Always returns 8 bits.
    """
    stripped_hex = _strip_hex(hex_value)
    # Bin doesn't return preleading 0's. So grab the expected length and add 0's as fill.
    hex_length = len(stripped_hex)
    binary = _strip_binary(bin(int(stripped_hex, 16)))
    binary_len = len(binary)
    if binary_len != hex_length * 4:
        return '0' * ((hex_length * 4) - binary_len) + binary
    else:
        return binary


def hex_to_decimal(hex_value):
    """ Converts the hex representation to decimal respresentation.

    Args:
        hex_value: Str value containing the hex representation with or without the 0x and/or spaces.

    Returns:
        Str value containing the decimal respresentation.
    """
    return str(int(_strip_hex(hex_value), 16))


def hhz_to_mhz(hhz):
    """ Converts hHz to MHz.

    Args:
        hhz: Str value containing the frequency in hHz (HectoHertz)

    Returns:
        Str value of the frequency in MHz (MegaHertz)
    """
    return str(float(hhz) * 10 ** -4)


def hz_to_mhz(hz):
    """ Converts Hz to MHz.

    Args:
        hz: Str value containing the frequency in Hz (Hertz)

    Returns:
        Str value of the frequency in MHz (MegaHertz)
    """
    return str(float(hz) * 10 ** -6)


def kbaud_to_baud(kbaud):
    """ Converts kbaud to bauds.

    Args:
        kbaud: Str value containing kbaud (kilo symbols per second)

    Returns:
        Str value of baud (symbols per second)
    """
    return str(float(kbaud) * 10 ** 3)


def mhz_to_hz(mhz):
    """ Converts MHz to Hz.

    Args:
        mhz: Str value containing the frequency in MHz (MegaHertz)

    Returns:
        Str value of the frequency in Hz (Hertz)
    """
    return str(float(mhz) * 10 ** 6)


def mhz_to_hhz(mhz):
    """ Converts MHz to hHz.

    Args:
        mhz: Str value containing the frequency in MHz (MegaHertz)

    Returns:
        Str value of the frequency in hHz (HectoHertz).
    """
    return str(float(mhz) * 10 ** -4)


# Allows testing with string_conversions.py <conversion_function> <string_value>
if __name__ == '__main__':
    args = _parse_args()
    print(globals()[args.conversion](args.string_value))
