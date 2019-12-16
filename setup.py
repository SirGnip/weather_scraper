import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="weather_scraper",
    version="0.0.1",
    description="A personal project to download historical weather data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SirGnip/weather_scraper",

    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    python_requires='>=3.7',
    install_requires=[
        # 3rd party dependencies
        'darksky_weather==1.3.1',
        'pylint==2.4.4',
        'mypy==0.750',
    ],
)
