from setuptools import setup, Extension
import numpy

permanentModule = Extension('qlab.utils.permanent',
                       sources=['qlab/utils/src/qlabmodule.c'],
                       extra_compile_args=["-Ofast", "-march=native"],
                       include_dirs=[numpy.get_include()])

setup(
    name='qlab',
    version='1.0.1',
    description='qlab is a Python package that provides methods useful to the Quantum Information Lab @ La Sapienza.',
    author='Matteo Pompili',
    author_email='matpompili@gmail.com',
    license='GNU',
    url='https://github.com/matpompili/qlab/',
    download_url='https://github.com/matpompili/qlab/archive/v1.0.1-beta.tar.gz',
    classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: Implementation :: CPython',
    'Topic :: Scientific/Engineering :: Physics'
    ],
    packages=['qlab.controllers', 'qlab.utils'],
    ext_modules=[permanentModule],
    install_requires=['numpy', 'pyvisa']
)
