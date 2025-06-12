"""
Setup script for PDF Reader application.
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="pdf-reader",
    version="1.0.0",
    description="A modern PDF reader application built with PyQt6 and PyMuPDF",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/pdf-reader",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-qt>=4.0',
            'black>=21.0',
            'flake8>=3.9',
            'mypy>=0.900',
        ],
        'test': [
            'pytest>=6.0',
            'pytest-qt>=4.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'pdf-reader=pdf_reader.__main__:main',
        ],
        'gui_scripts': [
            'pdf-reader-gui=pdf_reader.__main__:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business",
        "Topic :: Multimedia :: Graphics :: Viewers",
    ],
    keywords="pdf reader viewer pyqt6 pymupdf",
    include_package_data=True,
    package_data={
        'pdf_reader': [
            'assets/*',
            'assets/icons/*',
            'assets/themes/*',
        ],
    },
)
