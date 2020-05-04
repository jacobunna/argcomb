"""Installation for ArgComb. """

import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="argcomb",
    version="0.1",
    description="Validate the argument combination passed to a function",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jacobunna/argcomb",
    author="Jacob Unna",
    author_email="jacob.unna@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English ",
        "Typing :: Typed",
    ],
    keywords="argument parameter validation",
    py_modules=["argcomb"],
    python_requires=">=3.8",
    extras_require={"test": ["pytest"]},
)
