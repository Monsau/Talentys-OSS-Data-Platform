#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for Dremio + dbt + OpenMetadata Integration
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="talentys-data-platform",
    version="1.1.0",
    author="Mustapha Fonsau",
    author_email="support@talentys.eu",
    description="Talentys Data Platform - Enterprise Data Engineering & Analytics with AI-powered Chat UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Monsau/data-platform-iso-opensource",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="dremio dbt openmetadata superset airbyte data-platform analytics ai chat-ui rag",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "ai": [
            "streamlit>=1.28.0",
            "langchain>=0.1.0",
            "chromadb>=0.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "talentys-orchestrate=orchestrate_platform:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Monsau/data-platform-iso-opensource/issues",
        "Documentation": "https://github.com/Monsau/data-platform-iso-opensource/blob/main/README.md",
        "Source": "https://github.com/Monsau/data-platform-iso-opensource",
    },
)
