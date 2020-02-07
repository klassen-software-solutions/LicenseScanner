from setuptools import setup, find_namespace_packages

setup(
    python_requires='>=3.7',
    packages=find_namespace_packages(include=["kss.*"]),
    package_data={'kss.license': ['resources/*']},
)
