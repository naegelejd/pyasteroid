from distutils.core import setup, Extension

vector = Extension("vector", sources=["vectormodule.c"])

setup(
    name = "vector",
    version = '0.0.2',
    author =  "Joseph Naegele",
    author_email = "joseph.naegele@gmail.com",
    description = "A basic 2D vector class.",
    license = "MIT",
    keywords = "vector 2D",
    ext_modules=[vector]
)
