from setuptools import setup

setup(
    name='django-data-mover',
    version='0.1.1dev',
    author='Gabriel Grant',
    packages=['data_mover', 'data_mover.management', 'data_mover.management.commands'],
    license='LGPL',
    long_description=open('README').read(),
    install_requires=[
        'django',
        'django-filepathfield-migrator',
    ],
    dependency_links = [
    	'http://github.com/gabrielgrant/django-filepathfield-migrator/tarball/master#egg=django-filepathfield-migrator',
    ]
)

