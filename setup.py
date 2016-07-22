#from distutils.core import setup
#from setuptools import find_packages
#from distutils.core import Extension
from setuptools import find_packages
from distutils.core import setup
setup(
    name = 'obnpy',
    packages = find_packages(),
    version = '0.4',
    description = 'Python interface for OpenBuildNet node',
    author = 'altugb',
    author_email = 'altug.bitlislioglu@epfl.ch',
    url = 'https://altugb@bitbucket.org/altugb/obnpy.git',    
)


    # py_modules=['obnnode'],    
    # package_data={'': ['libobnext-mqtt.dylib','extra.txt']},
    # include_package_data=True,
    # install_requires=[],

#package_dir = {'': 'src'}
#libraries = [('.',{'':'libobnext-mqtt.dylib'})],
#data_files=[('libc',['/libobnext-mqtt.dylib']), ('libc',['/extra.txt'])],