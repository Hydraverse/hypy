from distutils.core import setup
import pkg_resources
import pathlib
import hydra
import re

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement)
        for requirement
        in pkg_resources.parse_requirements(requirements_txt)
    ]

setup(
    name="hypy",
    version="1.1.1",
    description=hydra.__doc__,
    author="Halospace Foundation",
    author_email="contact@halospace.org",
    url="https://github.com/hydraverse/hypy",
    install_requires=install_requires,
    packages=["hydra", "hydra.app", "hydra.rpc", "hydra.res", "hydra.test", "hydra.test.app", "hydra.util"],
    package_data={
        "hydra": [
            "res/*"
        ],
    },
    entry_points=dict(
        console_scripts=[
            "hy = hydra.hy:Hydra.main",
            "hy-cli = hydra.app.cli:HydraCLIApp.main",
            "hy-rpc = hydra.app.rpc:HydraRPCApp.main",
            "hy-test = hydra.test:Test.main",
        ]
    )
)
