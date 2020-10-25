import setuptools
import json

install_requires = []

with open("Pipfile.lock") as fd:
    lock_data = json.load(fd)
    install_requires = list(lock_data["default"].keys())

setuptools.setup(
    name="cactus",
    version="0.1",
    description="SQL formatter",
    url="https://github.com/tkokan/cactus",
    author="Tonci Kokan",
    author_email="tkokan@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'cactus = cactus.main:main',
        ],
    }
)
