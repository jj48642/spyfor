from setuptools import setup, find_packages

setup(
    name='spyfor',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Stata Regression Formatter',
    long_description=open('README.md').read(),
    install_requires=['pandas', 're'],
    url='https://github.com/jj48642/spyfor',
    author='James J Anderson',
    author_email='jj48642@gmail.com'
)