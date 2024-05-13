from setuptools import  setup

setup(
    name = 'nimble',
    description = 'Python module for generating any nimble configuration',
    packages=['nimble_orchestration', 'nimble_builder'],
    version = '0.0.1',
    install_requires=[
        'cadquery>=2',
        'cadscript>=0.5.2',
        'exsource-tools',
        'cq-cli @ git+https://github.com/CadQuery/cq-cli.git',
        'gitbuilding'
    ]
)