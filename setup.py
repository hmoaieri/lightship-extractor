from setuptools import setup, find_packages

setup(
    name="lightship-extractor",
    version="1.0.0",
    description="Reverse engineering of lightship weight distribution from loading manual data.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["numpy>=1.24.0", "scipy>=1.10.0", "matplotlib>=3.7.0"],
    python_requires=">=3.8",
)
