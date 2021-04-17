import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="objectscriber",
    version="0.0.4",
    author="Sergiy Popovych",
    author_email="sergiy.popovich@gmail.com",
    description="A simple tool for flexible serialization and desiarelization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/supersergiy/objectscriber",
    include_package_data=True,
    package_data={'': ['*.py']},
    install_requires=[
      'six',
    ],
    packages=setuptools.find_packages(),
)
