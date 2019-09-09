from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="pyrameters",
    version="0.0.1",
    description="Turbocharged parametrized testing. Drop-in replacement for `@pytest.mark.parametrize`.",
    long_description=long_description,
    classifiers=[],
    keywords="",
    author="Tony Lykke",
    author_email="hi@tonylykke.com",
    url="https://github.com/roganartu/pyrameters",
    license="TBA",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    extras_require={"test": ["pytest", "hypothesis"]},
)
