""" Conversions based around getting a datetime object out of a str value.

__functions__:
    _parse_args
    str_to_datetime

@author: dcsteve24
__python__version__ = 'Py2/Py3'
__os__ = All
__updated__ = '2021-09-05'
"""

from argparse import ArgumentParser
from datetime import datetime

# A list of the conversion function present. For use as value checks.
ACCEPTABLE_TIME_CONVERSIONS = ['str_to_datetime']


# Contains str time formats we've come across so far. Add as needed.
STR_TIME_FORMATS = ['%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d']


def _parse_args():
    """ Uses ArgumentParser to parse in the passed arguments. """
    parser = ArgumentParser(description='Convert a string value and return the converted string'
                            ' value')
    parser.add_argument('conversion', choices=ACCEPTABLE_TIME_CONVERSIONS, help='The conversion to'
                        ' perform')
    parser.add_argument('string_value', help='The original value to convert as a string')
    return parser.parse_args()


def str_to_datetime(string):
    """ Converts a string into a datetime object.

    Args:
        string: The value we want to convert

    Returns:
        datetime object based on the string value passed
    """
    # Need to match the largest first or we could get an unexpected value.
    STR_TIME_FORMATS.sort(key=len, reverse=True)
    for time_format in STR_TIME_FORMATS:
        try:
            return datetime.strptime(string, time_format)
        except ValueError:
            pass
    raise ValueError(
        'Could not find a timestamp match for %s. Add a matching time format.' % string)


# Allows testing with datetime_conversions.py <conversion_function> <string_value>
if __name__ == '__main__':
    args = _parse_args()
    print(globals()[args.conversion](args.string_value))
