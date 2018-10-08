import subprocess

# if you care about the cmd output use call
def call(cmd):
    pipes = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = pipes.communicate()
    if pipes.returncode != 0:
        # an error happened!
        # err_msg = "%s. Code: %s" % (std_err.strip(), pipes.returncode)
        raise GigalixirShellError(pipes.returncode, cmd, output=std_out, stderr=std_err)
    return std_out.decode("utf-8").strip()


# if you only care that the cmd succeeded, call this
def cast(cmd):
    return subprocess.check_call(cmd.split())

class GigalixirShellError(subprocess.CalledProcessError):
    def __init__(self, returncode, cmd, output=None, stderr=None):
        self.stderr = stderr
        super(GigalixirShellError, self).__init__(returncode, cmd, output=output)

    def __str__(self):
        if self.returncode and self.returncode < 0:
            try:
                return "Command '%s' died with %r. Output: '%s' stderr: '%s'" % (
                        self.cmd, signal.Signals(-self.returncode), self.output, self.stderr)
            except ValueError:
                return "Command '%s' died with unknown signal %d. Output: '%s' stderr: '%s'" % (
                        self.cmd, -self.returncode, self.output, self.stderr)
        else:
            return "Command '%s' returned non-zero exit status %d. Output: '%s' stderr: '%s'" % (
                    self.cmd, self.returncode, self.output, self.stderr)


