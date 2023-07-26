#!/usr/bin/env python
# -*- coding: utf-8 -*-

# import distribute_setup
# distribute_setup.use_setuptools()
from setuptools import setup

setup(
    name="Eyecandy",
    version="0.1",
    description="Eyecandy - ASS effect generator",
    long_description=open("README", encoding="utf-8").read(),
    url="https://bitbucket.org/alquimista/eyecandy",
    download_url="https://bitbucket.org/alquimista/eyecandy/downloads",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        'Topic" :: Artistic Software',
        "Topic :: Multimedia",
        "Topic :: Text Processing",
    ],
    author="Roberto Gea (Alquimista)",
    author_email="alquimistaotaku@gmail.com",
    license="MIT",
    packages=["eyecandy"],
    entry_points={"console_scripts": ["eyecandy = eyecandy.helpers:generate_effect"]},
    zip_safe=False,
    keywords="eyecandy text karaoke .ass",
)
