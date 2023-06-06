from setuptools import setup, find_packages


setup(
    name="spepper",
    version="0.0.1",
    description="enforce style like syntax",
    packages=find_packages(),
    install_requires=["pycodestyle"],
)
