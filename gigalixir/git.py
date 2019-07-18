import os
import subprocess

def check_for_git():
    try:
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_call('git rev-parse --is-inside-git-dir'.split(), stdout=FNULL, stderr=subprocess.STDOUT)
    except OSError as e:
        # from https://stackoverflow.com/a/11210185/365377
        if e.errno == os.errno.ENOENT:
            raise Exception("Sorry, we could not find git. Try installing it and try again.")
        else:
            raise
    except subprocess.CalledProcessError:
        raise Exception("You must call this from inside a git repository.")

