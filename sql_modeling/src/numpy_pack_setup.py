import setuptools
from setuptools.extension import Extension
#import version
version = "0.0.3"

with open("README.md", "r") as fh:
    long_description = fh.read()
    ext_name = "laser_numpy_model"

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

setuptools.setup(
    name=ext_name,
    #version=version.__version__,
    version,
    author="Jonathan B",
    author_email="jbloedow@idmod.org",
    description="IDM's Lightning Fast Next-Generation Agent-Based Modeling Prototype",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InstituteforDiseaseModeling/laser",
    #packages=setuptools.find_packages(exclude=['laser_sql_model/*']),
    packages=['laser_numpy_model'],
    package_data={'laser_numpy_model': ['makefile', 'eula_preproc.sh']},
    entry_points={
        'console_scripts': [
            'laser_numpy_model.bootstrap=laser_numpy_model.bootstrap:main',
        ],
    },
    #include_package_data=True,
    setup_requires=['wheel'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
