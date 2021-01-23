#!/usr/bin/env python

from setuptools import setup

setup(name='snap-combine',
        version='0.1',
        description='SuperNova Async Pipeline: combining',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        packages=['snap.combine','snap.util','snap.client'],
        py_modules=['snap.datablock'],
        install_requires=['numpy','pandas',
                          'snap-base >=1.0.1',
                          'sn_stat',
        ]
     )

