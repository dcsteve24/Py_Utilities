""" Pulss the current lsistener ports of a host and picks the first usable port within a desired
range

__classes__:
    NoCommandFoundError
    NoPortsFound

__functions__:
    pick_port

@author: dcsteve24
__python_version__ = Py2/Py3
__os__ =  Linux
__updated__ = '2021-09-04'
"""

import re
import subprocess

from .remote_linux_commands import remote_operations


class NoCommandFoundError(Exception):
    pass


class NoPortsFound(Exception):
    pass


def pick_port(host,
              port_min,
              port_max,
              ssh_port=22):
    """ Picks an unused port within the desired range (min, max) and returns it

    This command will ssh into the passed host, pull the open listening ports, and then pick
    the first usable port within the desired range.

    Args:
        host: Str. The host we are grabbing the port range from. CAn be an IP or hostname.
        port_min: The lowest acceptable port number in the desired range.
        port_max: The highest acceptable port number in the desired range.

        Optional:
            ssh_port: The port to use for SSH connectivity. Not used if host is set to 'local' or
                None.

    Returns:
        The found unused port within the range. If one is not found, this returns None.
    """
    # Build a list of current listener ports
    command = ['netstat -tulnp']
    if host is None or 'local' in host:
        subp = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, universal_newlines=True, buffsize=0)
        results = subp.stdout.readlines()
        subp.terminate()
    else:
        results = remote_operations(remote_host=host, commands=command, port=ssh_port,
                                    catch_errors=False, tty_session=True)
    str_results = ', '.join(results)
    if 'command not found' in str_results:
        raise NoCommandFoundError('netstats is not installed on the %s device. Please install it'
                                  ' and try again' % host)
    else:
        for port in range(port_min, port_max):
            if not re.search(str(port), results):
                return port
    return None
