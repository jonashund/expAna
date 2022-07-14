import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="expAna",
    version="0.0.1",
    author="Jonas Hund",
    author_email="jonas.hund@gmx.de",
    description="Analyse your experimental data acquired with the IFM lab equipment.",
    url="https://github.com/jonashund/expAna",
    packages=["expAna"],
    package_dir={"expAna": "expAna"},
    install_requires=[
        "istra2py",
        "muDIC",
        "numpy",
        "matplotlib",
        "dill",
        "xlrd",
        "noise",
        "openpyxl",
    ],
    extras_require={"test": ["pytest",]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
