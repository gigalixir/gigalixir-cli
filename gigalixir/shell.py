import subprocess

# if you care about the cmd output use call
def call(cmd):
    return subprocess.check_output(cmd.split()).strip()

# if you only care that the cmd succeeded, call this
def cast(cmd):
    return subprocess.check_call(cmd.split())
