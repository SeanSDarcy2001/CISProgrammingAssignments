import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ciscode",
    version="0.0.0",
    author="Alexandra Szewc, Seby Darcy",
    author_email="aszewc1@jhu.edu",
    description="PA3 Programming Assignment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["numpy", "scipy", "rich", "click"],
    include_package_data=True,
    python_requires=">=3.9",
)
