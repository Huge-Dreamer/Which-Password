from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="which-password",
    version="2.0.0",
    author="Which-Password Team",
    author_email="which-password@example.com",
    description="A powerful and efficient password-protected archive cracker",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/which-password/Which-Password",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: System :: Archiving :: Compression",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "which-password=src.which_password:main",
        ],
    },
    package_data={
        "config": ["config.json.example"],
    },
    include_package_data=True,
) 