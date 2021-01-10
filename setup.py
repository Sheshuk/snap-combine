#!/usr/bin/env python

from setuptools import setup

setup(name='snap-combine',
        version='0.1',
        description='SuperNova Async Pipeline: combining',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        packages=['snap.combine','snap.util'],
        install_requires=['numpy','pandas',
                          'snap-base @ https://github.com/Sheshuk/snap-base/archive/v0.1.tar.gz',
                          'sn_stat @ https://github.com/Sheshuk/sn_stat/archive/v0.1.tar.gz',
        ]
     )

