from setuptools import setup, find_packages

version = "0.0.1.dev0"

lib_folder = os.path.dirname(os.path.realpath(__file__))
req_path = os.path.join(lib_folder, "/requirements.txt")
install_requires = []

if os.path.isfile(req_path):
    with open(req_path) as f:
        install_requires = f.read().splitlines()

with open('README.md') as f:
    README = f.read()

setup(
    name='capabilities-reader',
    version=version,
    description='PDOK (OGC) capabilities documents reader',
    long_description=README,
    author='Anton Bakker',
    author_email='anton.bakker@kadaster.nl',
    packages=find_packages(exclude=('tests', 'docs')),
    setup_requires=['wheel'],
    install_requires=install_requires,
    entry_points='''
        [console_scripts]
        read-cap=capabilities_reader.cli:main
        read-capabilities=capabilities_reader.cli:main
    ''',
)
