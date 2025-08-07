#!/usr/bin/env python3
"""
Setup script for Guitar Chord Fingering Generator

This creates an installable package that includes both the CLI tool
and the MCP server as standalone executables.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Professional guitar chord fingering generator with AI integration"

setup(
    name="guitar-chord-generator",
    version="1.0.0",
    description="Professional guitar chord fingering generator with AI integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Guitar Chord Generator",
    author_email="developer@example.com",
    url="https://github.com/username/fretboard-diagram-generator",
    
    # Package configuration
    packages=find_packages() + ['.'],
    py_modules=['cli', 'mcp_server'],
    package_data={
        'src': ['*.py'],
    },
    include_package_data=True,
    
    # Dependencies
    install_requires=[
        'matplotlib>=3.5.0',
        'click>=8.0.0',
        'mcp>=1.12.0',
    ],
    
    # Python version requirement
    python_requires='>=3.10',
    
    # Entry points for command-line tools
    entry_points={
        'console_scripts': [
            'guitar-chord-cli=cli:cli',
            'guitar-chord-mcp-server=mcp_server:run_server',
        ],
    },
    
    # Classification
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Musicians',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Sound/Audio :: MIDI',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    
    # Additional metadata
    keywords='guitar, chords, music, theory, fingerings, diagrams, mcp, ai',
    project_urls={
        'Bug Reports': 'https://github.com/username/fretboard-diagram-generator/issues',
        'Source': 'https://github.com/username/fretboard-diagram-generator',
        'Documentation': 'https://github.com/username/fretboard-diagram-generator/blob/main/README.md',
    },
)