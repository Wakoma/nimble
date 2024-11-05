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
        # 'cadquery>=2',
        'cadquery @ git+https://github.com/CadQuery/cadquery.git',
        'cadquery-png-plugin @ git+https://github.com/jmwright/cadquery-png-plugin.git',
        'cadscript>=0.5.2',
        'exsource-tools',
        'cq-cli @ git+https://github.com/CadQuery/cq-cli.git',
        'gitbuilding==0.15.0a4',
        'cq-annotate @ git+https://github.com/jmwright/cq-annotate.git',
        'cq_warehouse @ git+https://github.com/gumyr/cq_warehouse.git',
        'cadorchestrator>=0.0.3'
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
