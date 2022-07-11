import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="expAna",
    version="0.0.1",
    author="Jonas Hund",
    author_email="jonas.hund@kit.edu",
    description="Analyse your experimental data acquired in the IFM laboratory.",
    url="https://git.scc.kit.edu/ifm/labor/exputil/expAna",
    packages=["expAna"],
    package_dir={"expAna": "expAna"},
    # entry_points={"console_scripts": ["acquis2tif = expAna.console_scripts:acquis2tif_cmd"]},
    install_requires=[
        "istra2py",
        "expDoc",
        "muDIC",
        "numpy",
        "matplotlib",
        "dill",
        "xlrd",
        "noise",
        "openpyxl",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
