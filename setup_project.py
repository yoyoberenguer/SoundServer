# distutils: extra_compile_args = -fopenmp
# distutils: extra_link_args = -fopenmp

# USE :
# python setup_Project.py build_ext --inplace

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [Extension("SoundServer", ["SoundServer.pyx"],
                         extra_compile_args=['/openmp'],
                         extra_link_args=['/openmp']
                         )]

setup(
  name="MAPPING",
  cmdclass={"build_ext": build_ext},
  ext_modules=ext_modules
)