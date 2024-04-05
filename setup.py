from setuptools import setup, find_packages

setup(
    name='gigalixir',
    url='https://github.com/gigalixir/gigalixir-cli',
    author='Tim Knight',
    author_email='tim@gigalixir.com',
    version='1.12.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'certifi>=2024.2.2',
        'click>=8.1',
        'cryptography>=38.0',
        'pygments>=2.13',
        'pyOpenSSL>=22.1',
        'qrcode>=7.3',
        'requests>=2.28',
        'rollbar>=0.16',
        'setuptools>=69.0',
        'six>=1.16',
        'stripe>=4.1',
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
