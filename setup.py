"""
Simple setup script to install both nimble_orchestration and nimble_builder as packages
"""
from setuptools import  setup

setup(
    name = 'nimble',
    description = 'Python module for generating any nimble configuration',
    packages=['nimble_orchestration', 'nimble_builder'],
    version = '0.0.1',
    python_requires='>=3.10',
    install_requires=[
        'numpy~=1.26',
        'cadquery>=2',
        'cadscript>=0.5.2',
        'exsource-tools',
        'cq-cli @ git+https://github.com/CadQuery/cq-cli.git',
        'gitbuilding==0.15.0a2',
        'cq-annotate @ git+https://github.com/jmwright/cq-annotate.git',
        'cq_warehouse @ git+https://github.com/gumyr/cq_warehouse.git',
        'cadorchestrator @ git+https://gitlab.com/gitbuilding/cadorchestrator.git'
    ],
    extras_require={
        'dev': [
            'pylint',
            'colorama'
        ]
    },
    entry_points={'console_scripts': ['gen_nimble_conf_options = nimble_orchestration.gen_nimble_conf_options:main']}
)
