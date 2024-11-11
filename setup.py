from setuptools import setup, find_packages

setup(
    name="badorm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic==2.9.2",
        "pydantic_core==2.23.4",
        "typing_extensions==4.12.2",
        "annotated-types==0.7.0",
    ],
    author="Shiberal",
    author_email="francesco.grelli98@gmail.com",
    description="A simple SQLite operations package with Pydantic models",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Shiberal/badorm",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
) 