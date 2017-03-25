import os
import subprocess
import requests
from .shell import cast, call

def create(unique_name):
    try:
        # check for git folder
        with open(os.devnull, 'w') as FNULL:
            subprocess.check_call('git rev-parse --is-inside-git-dir'.split(), stdout=FNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        raise Exception("You must call this from inside a git repository.")

    unique_name = unique_name.lower()
    r = requests.post('http://localhost:4000/api/apps', headers = {
        'Content-Type': 'application/json',
    }, json = {
        "unique_name": unique_name,
    })
    if r.status_code != 201:
        raise Exception(r.text)
    else:
        # create the git remote
        cast('git remote add gigalixir https://git.gigalixir.com/%s.git/' % unique_name)
