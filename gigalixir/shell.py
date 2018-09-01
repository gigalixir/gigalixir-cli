import subprocess

# if you care about the cmd output use call
def call(cmd):
    # kind of crappy, but we call decode() here for python3 
    # compatibility. in python3 check_output returns a bytes-like
    # object which needs to be converted into a string.
    # for python2, it returns a string and calling decode() on it
    # gives you a unicode which is fine.
    pipes = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = pipes.communicate()
    if pipes.returncode != 0:
        # an error happened!
        # err_msg = "%s. Code: %s" % (std_err.strip(), pipes.returncode)
        raise Exception(std_out)
    return std_out.decode().strip()


# if you only care that the cmd succeeded, call this
def cast(cmd):
    return subprocess.check_call(cmd.split())
