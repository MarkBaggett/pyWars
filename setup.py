import setuptools

setuptools.setup(
    name="pywars", 
    version="5.0.3", 
    install_requires = ["requests >= 2.20.0", "rich >= 9.1.0"],
    license="All Rights Reserved. Do not distribute.",
    url="https://github.com/markbaggett/pyWars",
    packages=setuptools.find_packages(),
    author="MarkBaggett",
    author_email="mbaggett@sans.org",
    description="This software is exclusively for use with SANS SEC573 and SEC673",
    long_description="This software is exclusively for use with SANS SEC573 and SEC673",
    long_description_content_type="text/markdown",
    entry_points = {
        'console_scripts': ['pywars=pywars.__main__:main']
        },
    python_requires='>=3.6'
    )
