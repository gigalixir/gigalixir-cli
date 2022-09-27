from setuptools import setup, find_packages

setup(
    name='gigalixir',
    url='https://github.com/gigalixir/gigalixir-cli',
    author='Tim Day',
    author_email='tim@gigalixir.com',
    version='1.3.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.1',
        'requests>=2.28',
        'stripe>=4.1',
        'rollbar>=0.16',
        'pygments>=2.13',
        'qrcode>=7.3',
        'pyOpenSSL>=22.1',
        'cryptography>=38.0',
    ],
    entry_points='''
        [console_scripts]
        gigalixir=gigalixir:cli
    ''',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'HTTPretty',
        'sure',
    ],
    extras_require={
        'dev': [
            'Sphinx',
            'sphinx_rtd_theme',
            'sphinx-tabs',
        ],
        'test': [
            'pytest',
            'HTTPretty',
            'sure',
        ],
    }
)
