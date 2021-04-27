#from distutils.core import Extension
#from setuptools import find_packages
#from distutils.core import setup

from setuptools import setup

setup(
    name = 'obnpy2',
    packages=['obnpy2'],
    version = '1.0',
    description = 'Python client library for OpenBuildNet',
    author = 'nxtruong',
    author_email = 'truong.nghiem@gmail.com',
    url = 'https://github.com/nxt-lab/obnpy', 
    install_requires=['numpy',
                      ],
)

# py_modules=['obnnode'],    
# package_data={'': ['libobnext-mqtt.dylib','extra.txt']},
# include_package_data=True,
# install_requires=[],
#package_dir = {'': 'src'}
#libraries = [('.',{'':'libobnext-mqtt.dylib'})],
#data_files=[('libc',['/libobnext-mqtt.dylib']), ('libc',['/extra.txt'])],