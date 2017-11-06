from setuptools import find_packages, setup

setup(
    name="crawlster",
    version="0.0.1dev",

    description="None",
    long_description="None",

    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "colorlog",
        "cronex"
    ],
    test_require=[
        'pytest'
    ],
    test_suite='pytest'
)
