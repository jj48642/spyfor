from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='spyfor',
    version='0.0.2',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Stata Regression Formatter',
    long_description=open('README.md').read(),
    install_requires=['pandas', 'xlsxwriter'],
    url='https://github.com/jj48642/spyfor',
    author='James J Anderson',
    author_email='jj48642@gmail.com'
)