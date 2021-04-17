from setuptools import setup

DEPENDENCIES = open('requirements.txt', 'r').read().split('\n')
README = open('README.md', 'r').read()

setup(
    name='basedcrunch',
    version='1.0.0',
    description='Scraper for automating export of CrunchBase data.',
    long_description=README,
    long_description_content_type='text/markdown',
    author='HexOffender',
    author_email='HexOffender_1337@protonmail.com',
    url="http://github.com/",
    packages=['scraper'],
    entry_points={
        'console_scripts': ['basedcrunch = scraper.__main__:main']
    },
    install_requires=DEPENDENCIES,
    keywords=['security', 'network', 'CrunchBase', 'scraping'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)