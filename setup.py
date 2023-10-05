# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(

    name='corporate_espionage_the_game',

    description='Competition Project Entry',

    long_description=long_description,

    long_description_content_type='text/markdown',

    author='Reinier Zwikker, 4994388',

    packages=['assets'],

    include_package_data=True,

    python_requires='>=3.5, <4',

    install_requires=['pygame', 'numpy', 'pillow', 'pyopengl', 'pyopengl-accelerate'],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],

    entry_points={  # Optional
        'console_scripts': [
            'corporate-espionage-the-game=main:run',
        ],
    },
)