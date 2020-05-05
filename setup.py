"""Installation for ArgComb. """

import os

import setuptools

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="arg-comb",
    version="0.1",
    license="MIT",
    author="Jacob Unna",
    author_email="jacob.unna@gmail.com",
    description="Validate the argument combination passed to a function",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/jacobunna/argcomb",
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
    extras_require={"dev": ["pytest", "sphinx",]},
)
