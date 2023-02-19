import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION.txt", "r") as fh:
    version = fh.read().strip()

setuptools.setup(
    name='osf',
    version=version,
    author="Kevin Crouse",
    author_email="krcrouse@gmail.com",
    description="Encapsulating OSF REST entities as python classes/objects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
 )
