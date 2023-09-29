Testing
--

Last tested on ubuntu 22.04 (9/29/2023).

Install virtualenv
```
apt update
apt install python3-virtualenv
```

Setup virtualenv environment
```
virtualenv venv --python=python3
```

Enter environment
```
source venv/bin/activate
```

Upgrade/install pips
```
pip install --upgrade pip
pip install -e .[dev]
pip install -e .[test]
```

Run the tests
```
python setup.py test
```

When done, deactivate the virtualenv
```
deactivate
```
