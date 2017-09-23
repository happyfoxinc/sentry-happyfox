import os.path
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
    'requests>=1.0.0',
    'requests-oauthlib>=0.3.0'
]

dependency_links = [
    'git+ssh://git@github.com/getsentry/sentry-plugins.git@0.1.2#egg=sentry-plugins-0.1.2'
]

setup(
    name='sentry-happyfox',
    version='1.0.0',
    author='Aswin Murugesh',
    author_email='aswin@aswin.com',
    url='',
    description='A Sentry extension which integrates with Happyfox.',
    long_description=read('README.md'),
    license='BSD',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    zip_safe=False,
    install_requires=install_requires,
    dependency_links=dependency_links,
    include_package_data=True,
    entry_points={
        'sentry.apps': [
            'happyfox = sentry_happyfox',
        ],
        'sentry.plugins': [
            'happyfox = sentry_happyfox.plugin:HappyFoxPlugin'
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development'
    ],
)
