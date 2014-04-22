#from distutils.core import setup, Extension

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages, Extension

vector = Extension("asteroids.vector", sources=["src/vector/vectormodule.c"])

setup(
    name = "pyasteroid",
    version = '0.0.2',
    author =  "Joseph Naegele",
    author_email = "joseph.naegele@gmail.com",
    description = "A basic 2D vector class.",
    license = "MIT",
    keywords = "asteroids vector 2D",
    url="https://github.com/naegelejd/pyasteroid",
    install_requires = ['Pygame>=1.8'],
    packages=['asteroids'],
    package_data= {'':['*.png']},
    entry_points = {'console_scripts': ['asteroids = asteroids.main:main']},
    ext_modules=[vector],
)
