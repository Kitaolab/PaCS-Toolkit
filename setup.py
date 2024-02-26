from pathlib import Path

from setuptools import find_packages, setup

BASE_DIR = Path(__file__).resolve().parent
exec((BASE_DIR / "pacs/_version.py").read_text())

setup(
    name="pacs",
    version=__version__,  # type: ignore[name-defined]  # NOQA: F821
    packages=find_packages(),
    description=(
        "PaCS-ToolKit:",
        "Tool Kit for Parallel Cascade Selection Molecular Dynamic Simulation",
    ),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kitaolab",
    url="https://github.com/Kitaolab/PaCS-Toolkit",
    project_urls={
        "Source": "https://github.com/Kitaolab/PaCS-Toolkit",
        "Documentation": "",
        "Paper": "",
    },
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "numpy>=1.16.0",
    ],
    extras_require={
        "mdtraj": [
            "mdtraj>=1.9.9",
            "scipy>=1.7.3",
            "scikit-learn>=1.0.2",
        ],
        "msm": [
            "mdtraj>=1.9.9",
            "matplotlib>=3.5.3",
            "scipy>=1.7.3",
            "pandas>=1.1.5",
            # "pyemma>=2.5.12",
            "ipykernel>=6.16.2",
            "scikit-learn>=1.0.2",
        ],
        "all": [
            "mdtraj>=1.9.9",
            "scipy>=1.7.3",
            "scikit-learn>=1.0.2",
            "matplotlib>=3.5.3",
            "pandas>=1.1.5",
            # "pyemma>=2.5.12",
            "ipykernel>=6.16.2",
        ],
    },
    package_data={},
    entry_points={
        "console_scripts": [
            "pacs=pacs.__main__:main",
        ]
    },
)
