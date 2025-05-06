from setuptools import setup, find_packages
setup(
    name="policy_vqe",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "numpy", "networkx", "pyquil==4.2.0", "qcs-api-client==1.8.0"
    ],
)
