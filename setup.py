"""
Simple setup script to install the nimble_build_system as a package
"""
from setuptools import setup, find_packages

setup(
    name = 'nimble',
    description = 'Python module for generating any nimble configuration',
    packages=find_packages(),
    version = '0.0.1',
    python_requires='>=3.10',
    install_requires=[
        'numpy~=1.26',
        'cadquery==2.4.0',
        'cadquery_png_plugin==1.0.1',
        'cadscript>=0.5.2',
        'exsource-tools',
        'cadquery-cli==2.3.0',
        'cq_annotate',
        'cq_warehouse @ git+https://github.com/gumyr/cq_warehouse.git',
        'cadorchestrator>=0.1.0'
    ],
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
