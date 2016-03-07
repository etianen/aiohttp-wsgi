from setuptools import setup, find_packages


setup(
    name = "aiohttp-wsgi",
    version = "0.4.0",
    license = "BSD",
    description = "WSGI adapter for aiohttp.",
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "https://github.com/etianen/aiohttp-wsgi",
    packages = find_packages(exclude=("tests",)),
    install_requires = [
        "aiohttp>=0.21.2",
    ],
    extras_require = {
        "test":  [
            "pytest>=2.8.4",
            "pytest-cov>=2.2.0",
            "pytest-asyncio>=0.2.0",
        ],
    },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Django",
    ],
)
