from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

setup(
    name="iec870ree_moxa",
    version="0.2.1",
    author="GISCE-TI, S.L.",
    author_email="devel@gisce.net",
    description="Physical layer for using a Moxa devices with IEC870REE library",
    license='AGPL3',
    keywords="REE electric meters IEC 870-5-102",
    url="http://www.gisce.net",
    install_requires=[
        'iec870ree',
        'six',
    ],
    packages=find_packages(),
    long_description=readme,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Communications :: FIDO :: IEC 870-5-102",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
)
