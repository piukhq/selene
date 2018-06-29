from setuptools import setup

from app.version import __version__

setup(
    name='selene',
    version=__version__,
    description=('Transaction matching merchant ID processor. Massages merchant '
                 'ID data into a homogeneous format accepted by Hephaestus.'),
    url='https://git.bink.com/Olympus/selene',
    author='Chris Latham',
    author_email='cl@bink.com',
    zip_safe=True)
