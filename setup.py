from setuptools import setup, find_packages

setup(
    name='gigalixir',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click~=6.7',
        'requests~=2.13.0',
        'stripe~=1.51.0',
        'rollbar~=0.13.11',
    ],
    entry_points='''
        [console_scripts]
        gigalixir=gigalixir:cli
    ''',
    setup_requires=[
        'pytest-runner',
        'HTTPretty',
    ],
    tests_require=[
        'pytest',
    ],
)
