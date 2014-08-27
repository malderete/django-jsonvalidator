from setuptools import setup, find_packages

import jsonvalidator


setup(
    name='django-jsonvalidator',
    packages=['jsonvalidator'],
    version=jsonvalidator.__version__,
    description='Validates HTTP request with JSON data in Django.',
    long_description=open('README.md').read(),
    author='Martin Alderete',
    author_email='malderete@gmail.com',
    url='http://github.com/malderete/django-jsonvalidator',
    license='MIT',
    install_requires=['django', 'jsonschema==2.3.0'],
    include_package_data=True,
    package_data={'': ['README.md', 'LICENSE.txt']},
    zip_safe=False,
    keywords=['json', 'django', 'http'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

