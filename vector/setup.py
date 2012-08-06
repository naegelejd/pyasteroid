from distutils.core import setup, Extension

vector = Extension("vector", sources=["vectormodule.c"])

setup(
    name="vector",
    version='1.0',
    description="Provides a basic 2d vector object.",
    ext_modules=[vector]
)
