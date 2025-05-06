from setuptools import setup, find_packages
setup(
    name="hft_qbm",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy", "pandas", "qiskit==0.46.0"
    ],
)
