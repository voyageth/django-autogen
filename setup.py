from setuptools import setup, find_packages

setup(
    name="autogen_project",
    version="0.1.0",
    package_dir={"": ".github"},
    packages=find_packages(where=".github"),
    install_requires=[
        "openai",
        "PyGithub",
        "python-mcp",
    ],
)
