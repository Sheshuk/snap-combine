#!/usr/bin/env python
import setuptools 

with open('README.md') as f:
    readme = f.read()

setuptools.setup(name='snap-combine',
        version='0.6',
        description='SuperNova Async Pipeline: combining',
        long_description=readme,
        long_description_content_type='text/markdown',
        author='Andrey Sheshukov',
        author_email='ash@jinr.ru',
        packages=['snap.elements.combine','snap.elements.process','snap.elements.client'],
        py_modules=['snap.datablock'],
        install_requires=['numpy >= 1.19',
                          'snap-base[io] >=1.3.0',
                          'sn_stat >=0.3.2',
        ],
        extras_require={'doc':['sphinx', 'sphinx-rtd-theme']},
        python_requires='>=3.7'
     )

