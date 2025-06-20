from setuptools import setup, find_packages

setup(
    name="cde-harmonization",  # Your project name
    version="0.1.0",  # Version of your package
    description="Tool for generating LinkML schemas from CDE data",  # Short description
    #author="Your Name",  # Your name or the author of the project
    #author_email="your.email@example.com",  # Author's email address
    packages=find_packages(),  # or List of packages to include ["cde2linkml"]
    install_requires=[
        #"argparse",  # For argument parsing
        "pyyaml",  # For working with YAML files
        "pandas",  # For working with dataframes
        "requests",  # If you're fetching data via HTTP
        "curategpt",  # Install from PyPI
        "psutil",
    ],  # Dependencies for the project
    entry_points={
        "console_scripts": [
            "cde2linkml = cde2linkml.cli:main",  # Adjust this to your actual main function: Example CLI command: cde2linkml
        ]
    },
    python_requires='>=3.6',  # Python version compatibility
)
