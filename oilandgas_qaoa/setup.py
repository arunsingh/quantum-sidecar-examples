# oilandgas_qaoa/setup.py
from pathlib import Path
from setuptools import find_packages, setup

README = (Path(__file__).parent / "README.md").read_text()

setup(
    name="oilandgas_qaoa",
    version="0.1.0",
    description="Quantum QAOA feature-selection for seismic exploration",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Arun Singh",
    python_requires=">=3.10",
    packages=find_packages(),
    install_requires=[
        "cirq==1.2.0",
        "qcs-api-client==1.8.0",
        "numpy",
        "grpcio",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
