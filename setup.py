from setuptools import setup, find_packages

setup(
    name="dcm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-telegram-bot>=20.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "nltk>=3.6.0",
        "scikit-learn>=0.24.0",
        "python-dotenv>=0.19.0",
        "pytest>=6.2.0",
        "pytest-cov>=2.12.0",
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "pytest",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "dcm-bot=interface.telegram_bot:main",
        ]
    },
    python_requires=">=3.9",
    author="Edward Chiang",
    author_email="your.email@example.com",
    description="Dynamic Capital Management (DCM) System",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/dcm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
) 