import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ciscode",
    version="0.0.0",
    author="Benjamin D. Killeen",
    author_email="killeen@jhu.edu",
    description="Stuff",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=["numpy", "scipy", "rich", "click"],
    include_package_data=True,
    python_requires=">=3.9",
)
