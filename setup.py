import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='lgremote',
    version='0.1.0',
    author='pmqt',
    author_email='7368059+pmqt@users.noreply.github.com',
    description='LG WebOS TV Remote.',
    packages=['lgremote'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/pmqt/lgremote',
    install_requires=[
        'websockets',
        'netdisco',
        'wakeonlan'
    ],
    keywords=[
        'smarthome', 'smarttv', 'lg', 'tv', 'webos', 'remote'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
    ],
    entry_points={
        'console_scripts': [
            'lgremote=lgremote:main'
        ],
    },
)
