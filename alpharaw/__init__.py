#!python

try:
    from .sciex import SciexWiffData
    from .thermo import ThermoRawData
    from .ms_data_base import ms_reader_provider
except ImportError:
    pass

__project__ = "alpharaw"
__version__ = "0.0.2"
__license__ = "Apache"
__description__ = "An open-source Python package to unify raw MS data accession and storage."
__author__ = "Mann Labs"
__author_email__ = "opensource@alphapept.com"
__github__ = "https://github.com/MannLabs/alpharaw"
__keywords__ = [
    "bioinformatics",
    "software",
    "AlphaPept ecosystem",
    "mass spectrometry",
    "raw data",
    "data accession",
    "data storage"
]
__python_version__ = ">=3.8,<3.10"
__classifiers__ = [
    # "Development Status :: 1 - Planning",
    "Development Status :: 2 - Pre-Alpha",
    # "Development Status :: 3 - Alpha",
    # "Development Status :: 4 - Beta",
    # "Development Status :: 5 - Production/Stable",
    # "Development Status :: 6 - Mature",
    # "Development Status :: 7 - Inactive"
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]
__urls__ = {
    "Mann Labs at MPIB": "https://www.biochem.mpg.de/mann",
    "GitHub": __github__,
    # "ReadTheDocs": None,
    # "PyPi": None,
    # "Scientific paper": None,
}
__extra_requirements__ = {
    "development": "requirements_development.txt",
}
