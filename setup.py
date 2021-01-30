#!/usr/bin/env python

from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(name='snap-combine',
        version='0.5.3',
        description='SuperNova Async Pipeline: combining',
        long_description=readme,
        long_description_content_type='text/markdown',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        packages=['snap.combine','snap.util','snap.client'],
        py_modules=['snap.datablock'],
        install_requires=['numpy >= 1.19',
                          'snap-base >=1.0.1',
                          'sn_stat',
                          'tqdm >= 4.53',
        ]
     )

