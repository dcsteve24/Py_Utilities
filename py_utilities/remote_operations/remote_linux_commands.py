""" Contains the function(s) needed to run commands on other Linux machines via an SSH subprocess.

Requires:
    - the environment to have SSH keys in place so password authentication is not an issue.

__classes__:
    RemoteCommandError

__functions__:
    remote_operations

@author: dcsteve24
__python_version__ = Py2/Py3
__os__ =  Linux
__updated__ = '2021-09-04'
"""

import re
import subprocess


class RemoteCommandError(Exception):
    pass


def remote_operations(remote_host,
                      commands,
                      port=22,
                      catch_errors=True,
                      tty_session=False,
                      banner_size=0):
    """ Uses a SSH subprocess to run the passed command and returns the results.

    This function uses the subprocess module to conduct an SSH session on the remote machine. It
    then runs the passed commands in the order they are given. If catching errors, it will error if
    errors are found. It returns the output if it succeeds. This is left as a flag because current
    testing has shown that some cases have outputs thrown into stderr when they shouldn't be or we
    don't want them to be, so you can flip this to prevent false positive errors.

    This operates similarly to Ansible where it will SSH, run the commands, and provide back
    outputs.

    TODO: Passing in a command with a dollar sign ends up causing issues. Linux tries to evaluate
    the dollar sign as a variable which throws everything off. No amount of escapes ('\') seemed to
    work.

    TODO: Dig into improving this more. There is a lot of room for improvement regarding error
    handling and such.

    Args:
        remote_host: Str. The host we are going to SSH into. Can be an IP or hostname.
        commands: List. The commands you wish to perform as you would type them in a Linux session.

        Optional:
            port: Int. The SSH port to use. Defaults to 22.
            catch_errors: Bool. If True this will raise an error if the stderr has content. In
                some cases commands will generate data to stderr even when succeeding, in those
                cases we recommend swapping this to False and checking the results for expected
                outputs instead. Defaults to True
            tty_session: Bool. Determines if you want a tty session established while running
                commands. Setting this to True edits the ability to read outputs efficiently with
                current code. However, in cases where sudo is required, this needs to be flipped to
                True or the command will error. Defaults to False.
            banner_size: Int. Banners seem to get thrown into the stderr when logging in. This
                specifies how many lines to throw away so it doesn't raise a false positive.

    Returns:
        The results of the commands ran as a list based on each line returned.

    Raises:
        RemoteCommandError: Failed to either SSH, or while performing the commands.
    """
    if tty_session:
        ssh_command = ['ssh', remote_host, '-p', str(port), '-ttt']
        ssh_subprocess = subprocess.Popen(ssh_command, shell=False, stdin=subprocess.PIPE,
                                          universal_newlines=True, buffsize=0)
    else:
        ssh_command = 'ssh %s -p %s' % (remote_host, str(port))
        ssh_subprocess = subprocess.Popen(ssh_command, shell=True, stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          universal_newlines=True, buffsize=0)
    for command in commands:
        ssh_subprocess.stdin.write('%s\n' % command)
    if tty_session:
        result, error = ssh_subprocess.communicate('logout\n')
        if catch_errors and error:
            raise RemoteCommandError('\n'.join(error))
    else:
        ssh_subprocess.stdin.close()
        result = []
        for line in ssh_subprocess.stdout.readlines():
            # Without a shell these warnings can be seen in certain environments. So we ditch them.
            if re.match('Warning: no access to tty|Thus no job control in this shell', line):
                pass
            else:
                result.append(line)
        if catch_errors:
            error = ssh_subprocess.stderr.readlines()
            if banner_size:
                error = error[banner_size:]  # Throws away the banner
            if error:
                raise RemoteCommandError('\n'.join(error))
        ssh_subprocess.terminate()
    return result
