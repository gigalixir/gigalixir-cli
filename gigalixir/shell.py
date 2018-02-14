import subprocess

# if you care about the cmd output use call
def call(cmd):
    # kind of crappy, but we call decode() here for python3 
    # compatibility. in python3 check_output returns a bytes-like
    # object which needs to be converted into a string.
    # for python2, it returns a string and calling decode() on it
    # gives you a unicode which is fine.
    return subprocess.check_output(cmd.split()).decode().strip()

# if you only care that the cmd succeeded, call this
def cast(cmd):
    return subprocess.check_call(cmd.split())
