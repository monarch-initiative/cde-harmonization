from setuptools import setup, find_packages

setup(
    name="cde-harmonization",
    version="0.1.0",
    description="Tool for generating LinkML schemas from CDE data",
    #author="Your Name",
    #author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "pyyaml",    # YAML serialisation
        "pandas",    # DataFrame processing
        "openpyxl",  # Reading HEAL .xlsx files
        "requests",  # HTTP data fetching
        "curategpt",
        "psutil",
    ],  # Dependencies for the project
    entry_points={
        "console_scripts": [
            "cde2linkml = cde2linkml.cli:main",
        ]
    },
    python_requires=">=3.10",  # 3.10+ required for `dict | None` type union syntax
)
