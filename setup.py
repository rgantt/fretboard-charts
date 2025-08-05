#!/usr/bin/env python3
"""
Setup script for the Guitar Chord Fingering Generator CLI.
"""

from setuptools import setup, find_packages

setup(
    name='chord-generator',
    version='1.0.0',
    description='Guitar Chord Fingering Generator - Generate chord fingerings and diagrams',
    author='Guitar Chord Generator Team',
    python_requires='>=3.8',
    packages=find_packages(),
    install_requires=[
        'click>=8.0',
        'matplotlib>=3.5',
    ],
    entry_points={
        'console_scripts': [
            'chord-generator=cli:cli',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Musicians',
        'Topic :: Multimedia :: Sound/Audio',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
)