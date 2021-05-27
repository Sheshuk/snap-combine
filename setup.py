#!/usr/bin/env python

from setuptools import setup

setup(name='snap-combine',
        version='0.5.2',
        description='SuperNova Async Pipeline: combining',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        packages=['snap.elements.combine','snap.elements.process','snap.elements.client'],
        py_modules=['snap.datablock'],
        install_requires=['numpy >= 1.19',
                          'snap-base[io] >=1.3.0',
                          'sn_stat >=0.3.2',
                          'tqdm >= 4.53',
        ]
     )

