from os import path
from setuptools import setup, find_packages

pwd = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(pwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


def requirements_to_list(filename):
    return [dep for dep in open(path.join(pwd, filename)).read().split('\n') if (
        dep and not dep.startswith('#')
    )]


setup(
    name='wyreinvoicing',
    version='0.1.0',
    description='Invoicing API that creates a unique account for a user-generated invoice',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikeshultz/wyre-invoicing/wyre-invoicing-api',
    author='Mike Shultz',
    author_email='mike@mikeshultz.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Page Counters',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='ethereum invoicing api',
    packages=find_packages(exclude=['docs', 'tests', 'scripts', 'build']),
    install_requires=requirements_to_list('requirements.txt'),
    extras_require={
        'dev': requirements_to_list('requirements.dev.txt'),
    },
    entry_points={
        'console_scripts': [
            'wiapi=wyreinvoicing.api:main',
            'wiupdater=wyreinvoicing.updater:main',
            'widrain=wyreinvoicing.drain:main',
        ],
    },
    package_data={
        '': [
            'README.md',
        ]
    }
)
