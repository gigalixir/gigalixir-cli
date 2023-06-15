Testing
--

    # for python3 
    sudo apt-get install -y python3-venv
    sudo apt-get install -y python3-pip
    python3 -m venv venv3
    source venv3/bin/activate

    # Make sure you have pip >= 20.3
    # See https://pip.pypa.io/en/stable/topics/dependency-resolution/#backtracking
    pip3 install --upgrade pip
    pip3 install -e .[dev]
    pip3 install -e .[test]
    python setup.py test

    # hit a development server
    # get into the venv (see above)
    GIGALIXIR_ENV=dev gigalixir account
