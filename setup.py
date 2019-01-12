import setuptools  # type: ignore

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="jsonschemax",
    version="0.0.2",
    author="ocavue",
    author_email="ocavue@gmail.com",
    description="An implementation of JSON Schema for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ocavue/jsonschemax",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
