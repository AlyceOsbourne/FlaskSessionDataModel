from distutils.core import setup

setup(
    name='FlaskSessionDataModel',
    version='1',
    packages=['sessiondata'],
    url='https://github.com/AlyceOsbourne/FlaskSessionDataModel',
    license='GPLv3',
    author='Alyce Osbourne',
    install_requires=[
        'flask>=3.0.0',
        'bson>=0.5.10',
    ],
)