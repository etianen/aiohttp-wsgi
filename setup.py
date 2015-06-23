from setuptools import setup, find_packages


setup(
    name = "aiohttp-wsgi",
    version = "0.2.3",
    license = "BSD",
    description = "WSGI adapter for aiohttp.",
    author = "Dave Hall",
    author_email = "dave@etianen.com",
    url = "https://github.com/etianen/aiohttp-wsgi",
    packages = find_packages(),
    install_requires = [
        "aiohttp>=0.15.0",
    ],
    extras_require = {
        "test":  [
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
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
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Framework :: Django",
    ],
)
