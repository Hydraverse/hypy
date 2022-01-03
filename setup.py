from distutils.core import setup
import hydra
import re


setup(
    name="hypy",
    version="1.0.5",
    description=hydra.__doc__,
    author="Halospace Foundation",
    author_email="contact@halospace.org",
    url="https://github.com/hydraverse/hypy",
    requires=[re.split("[=<>~]+", line)[0].replace('-', '_') for line in open("requirements.txt").read().splitlines()],
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
