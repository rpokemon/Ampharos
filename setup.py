from setuptools import setup
import re

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = ""
with open("ampharos/__init__.py") as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("version is not set")

readme = ""
with open("README.rst") as f:
    readme = f.read()

setup(
    name="ampharos",
    author="bijij",
    url="https://github.com/bijij/ampharos",
    project_urls={
        "Documentation": "",
        "Issue tracker": "https://github.com/bijij/ampharos/issues",
    },
    version=version,
    packages=["ampharos"],
    license="MIT",
    description="Lightweight Pokemon Database",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    dependency_links=["http://github.com/bijij/donphan/master#egg=donphan"],
    install_requires=requirements,
    python_requires=">=3.6.0",
)
