from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cloud-comp-spy",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="一个基于Python的云计算网络竞争动态分析工具（仅开发用途）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cloud-comp-spy",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
) 