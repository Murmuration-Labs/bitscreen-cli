from setuptools import setup, find_packages
from io import open
from os import path

import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# automatically captured required modules for install_requires in requirements.txt
with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if ('git+' not in x) and (
    not x.startswith('#')) and (not x.startswith('-'))]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs \
                    if 'git+' not in x]
setup (
 name = 'bitscreen-cli',
 description = 'CLI client for BitScreen',
 version = '0.1.25',
 packages = find_packages(),
 install_requires = install_requires,
 python_requires='>=3.0',
 entry_points='''
        [console_scripts]
        bitscreen-cli=bitscreen_cli:app
    ''',
 author="Keyko",
 keyword="bitscreen, cli",
 long_description=README,
 long_description_content_type="text/markdown",
 dependency_links=dependency_links,
 classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ]
)
