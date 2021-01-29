#!/usr/bin/env python

from setuptools import setup

setup(name='snap-combine',
        version='0.5',
        description='SuperNova Async Pipeline: combining',
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

