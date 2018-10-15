import setuptools
import yaml

config = yaml.load(open("config.yml"))

with open(config["long_description_path"], "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=config["name"],
    version=config["version"],
    author=config["author"],
    author_email=config["author_email"],
    description=config["description"],
    long_description=long_description,
    long_description_content_type=config["long_description_content_type"],
    url=config["url"],
    packages=setuptools.find_packages(),
    classifiers=config["classifiers"],
    install_requires=[
        'matplotlib',
        'pyyaml',
        'numpy',
        'requests',
        'requests_oauthlib'
    ],
)