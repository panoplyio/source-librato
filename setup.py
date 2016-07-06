from distutils.core import setup

setup(
    name="panoply_librato",
    version="1.0.2",
    description="Panoply Data Source for the Librato API",
    author="Roi Avinoam",
    author_email="roi@panoply.io",
    url="http://panoply.io",
    install_requires=[
        "panoply-python-sdk"
    ],

    # place this package within the panoply package namespace
    package_dir={"panoply": ""},
    packages=["panoply.librato"]
)