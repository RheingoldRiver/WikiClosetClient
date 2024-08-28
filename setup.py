import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = "0.0.1"

setuptools.setup(
    name="WikiClosetClient",
    version=__version__,
    author="RheingoldRiver",
    author_email="river.esports@gmail.com",
    description="Tools for wiki.gg staff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RheingoldRiver/WikiClosetClient",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['mwcleric>=0.10.2']
)
