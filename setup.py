"""
Simple setup script to install the nimble_build_system as a package
"""
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name = 'nimble',
    description = 'Python module for generating any nimble configuration',
    packages=find_packages(),
    version = '0.0.1',
    python_requires='>=3.10',
    install_requires=requirements,
    extras_require={
        'dev': [
            'pylint',
            'colorama',
            'pytest'
        ]
    },
    entry_points={
        'console_scripts': [
            'gen_nimble_conf_options = nimble_build_system.utils.gen_nimble_conf_options:main',
            'nimble_devices_updater = nimble_build_system.utils.nimble_devices_updater:main'
        ]
    }
)
