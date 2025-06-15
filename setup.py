"""Setup script for Robot War game."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="robot-war",
    version="0.1.0",
    author="Robot War Development Team",
    description="A Python adaptation of 'La guerre des robots' (1985)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Currently no external dependencies
    ],
    entry_points={
        "console_scripts": [
            "robot-war=robot_war.main:main",
        ],
    },
)