from setuptools import setup, find_packages

with open('README.md') as f:
    README = f.read()

setup(
    name='capabilities-metadata-converter',
    version='0.1',
    description='PDOK Capabilities Metadata converter',
    long_description=README,
    author='Anton Bakker',
    author_email='anton.bakker@kadaster.nl',
    packages=find_packages(exclude=('tests', 'docs')),
    setup_requires=['wheel'],
    install_requires=[
        'lxml==4.2.1',
        'iso19119-nl-parser==0.0.2.dev0'
    ],
    entry_points='''
        [console_scripts]
        convert-cap=capabilities_md_converter.cli:main
        convert-capabilities=capabilities_md_converter.cli:main
    ''',
)
