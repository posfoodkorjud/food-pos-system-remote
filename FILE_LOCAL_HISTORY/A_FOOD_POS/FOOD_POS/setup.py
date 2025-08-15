#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Food POS System Setup Script
สคริปต์สำหรับติดตั้งและตั้งค่าระบบ POS สำหรับร้านอาหาร
"""

from setuptools import setup, find_packages
import os
import sys

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="food-pos-system",
    version="1.0.0",
    author="Food POS Developer",
    author_email="developer@foodpos.com",
    description="ระบบ POS สำหรับร้านอาหาร - Complete Point of Sale System for Restaurants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/foodpos/food-pos-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "black>=23.9.1",
            "flake8>=6.1.0",
        ],
        "printer": [
            "python-escpos>=3.0",
            "pyusb>=1.2.1",
        ],
        "gui": [
            "PyQt5>=5.15.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "food-pos=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "frontend": ["*.html", "css/*.css", "js/*.js"],
        "backend": ["*.py"],
    },
    keywords="pos, restaurant, point-of-sale, qr-code, promptpay, google-sheets",
    project_urls={
        "Bug Reports": "https://github.com/foodpos/food-pos-system/issues",
        "Source": "https://github.com/foodpos/food-pos-system",
        "Documentation": "https://github.com/foodpos/food-pos-system/wiki",
    },
)