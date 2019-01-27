import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="behavior",
    version="1.0",
    author="Hakan Kucukdereli",
    author_email="hkucukdereli@gmail.com",
    description="Analysis scripts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hkucukdereli/behavior",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
