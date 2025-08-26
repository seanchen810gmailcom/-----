#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
敲磚塊遊戲 - 安裝設定
"""

from setuptools import setup, find_packages
import os

# 讀取 README 檔案
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# 讀取需求檔案
def read_requirements():
    """讀取 requirements.txt"""
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements


setup(
    name="breakout-game",
    version="2.0.0",
    author="遊戲開發者",
    author_email="developer@example.com",
    description="一個使用 Pygame 開發的敲磚塊遊戲，具有 TNT 爆炸功能",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/breakout-game",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Arcade",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "coverage>=6.0",
            "flake8>=4.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
        ],
        "docs": [
            "Sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "breakout-game=main_new:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
        "assets": ["images/*", "sounds/*"],
        "docs": ["*.md", "*.rst"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/breakout-game/issues",
        "Source": "https://github.com/yourusername/breakout-game",
        "Documentation": "https://breakout-game.readthedocs.io/",
    },
)
