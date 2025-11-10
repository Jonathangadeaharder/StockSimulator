#!/usr/bin/env python3
"""
StockSimulator setup configuration
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    req_file = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(req_file):
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f
                   if line.strip() and not line.startswith('#') and not line.startswith('-r')]
    return []

setup(
    name="stocksimulator",
    version="1.0.0",
    author="StockSimulator Contributors",
    author_email="",
    description="A production-grade stock market simulation and backtesting platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jonathangadeaharder/StockSimulator",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
    },
    entry_points={
        "console_scripts": [
            "stocksim-optimize=historical_data.find_optimal_allocation:main",
            "stocksim-percentile=historical_data.percentile_performance_analysis:main",
            "stocksim-risk=historical_data.risk_adjusted_allocation:main",
            "stocksim-detailed=historical_data.detailed_leverage_table:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Jonathangadeaharder/StockSimulator/issues",
        "Source": "https://github.com/Jonathangadeaharder/StockSimulator",
    },
)
