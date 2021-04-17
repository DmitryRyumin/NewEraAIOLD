import sys

from setuptools import setup, find_packages

MIN_PYTHON_VERSION = (3, 8)

if sys.version_info[:2] < MIN_PYTHON_VERSION:
    raise RuntimeError('Python version required = {}.{}'.format(MIN_PYTHON_VERSION[0], MIN_PYTHON_VERSION[1]))

import neweraai

REQUIRED_PACKAGES = [
    'torch >= 1.8.1',
    'torchaudio >= 0.8.1',
    'SoundFile >= 0.10.3.post1',
    'numpy >= 1.20.2',
    'pandas >= 1.2.4',
    'matplotlib >= 3.4.1',
    'jupyterlab >= 3.0.14',
    'pymediainfo >= 5.0.4',
    'requests >= 2.25.1',
    'vosk >= 0.3.21',
    'seaborn >= 0.11.1'
]

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Natural Language :: Russian
Natural Language :: English
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: Implementation :: CPython
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Mathematics
Topic :: Scientific/Engineering :: Artificial Intelligence
Topic :: Software Development
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX :: Linux
"""

with open('README.md', 'r') as fh:
    long_description = fh.read()

    setup(
        name = neweraai.__name__,
        packages = find_packages(),
        license = neweraai.__license__,
        version = neweraai.__version__,
        author = neweraai.__author__,
        author_email = neweraai.__email__,
        maintainer = neweraai.__maintainer__,
        maintainer_email = neweraai.__maintainer_email__,
        url = neweraai.__uri__,
        description = neweraai.__summary__,
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        install_requires=REQUIRED_PACKAGES,
        keywords = ['NewEraAI', 'MachineLearning', 'Statistics', 'ComputerVision', 'ArtificialIntelligence',
                    'Preprocessing'],
        include_package_data = True,
        classifiers = [_f for _f in CLASSIFIERS.split('\n') if _f],
        python_requires = '>=3.8, <4',
        entry_points = {
            'console_scripts': [],
        },
        project_urls = {
            'Bug Reports': 'https://github.com/DmitryRyumin/NewEraAI/issues',
            'Documentation': 'https://github.com/DmitryRyumin/NewEraAI',
            'Source Code': 'https://github.com/DmitryRyumin/NewEraAI/tree/main/neweraai',
            'Download': 'https://github.com/DmitryRyumin/NewEraAI/tags',
        },
    )
