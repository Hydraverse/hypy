import sys
import os

from setuptools import find_packages
from setuptools import setup

import hydra


# noinspection Assert
assert sys.version_info[0] == 3 and sys.version_info[1] >= 8, "rpc_proxy requires Python 3.8 or newer"

setup(
    name="halo-hypy",
    url="https://github.com/hydraverse/hypy",
    author="Halospace Foundation",
    author_email="contact@halospace.org",
    version=hydra.VERSION,
    description=" // ".join(hydra.__doc__.splitlines()),
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "hydra": [
            "res/*"
        ],
    },
    install_requires=[
        "pytest>=6.2.5",
        "argcomplete>=1.12.3",
        "requests>=2.26.0",
        "attrdict",
        "pytz",
        "pycryptodome",
    ],
    entry_points={
        "console_scripts": [
            "hy = hydra.hy:Hydra.main",
            "hycli = hydra.app.cli:HydraCLIApp.main",
            "hytest = hydra.test:Test.main",
            "peerscan = hydra.app.peerscan:PeerScan.main",
            "hytop = hydra.app.top:TopApp.main",
        ]
    },
)
