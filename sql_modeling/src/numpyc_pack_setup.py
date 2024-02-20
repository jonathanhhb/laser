import setuptools
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext
#import version
version = "0.0.3"

with open("README.md", "r") as fh:
    long_description = fh.read()
    ext_name = "laser_numpyc_model"

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().split("\n")

numpyc = Extension('update_ages', sources=['update_ages.c'])
class CustomBuildExt(build_ext):
    def run(self):
        # Build the C extension module
        build_ext.run(self)
        # Call the base class run() method
        if not self.inplace:
            self.build_extension(numpyc)


setuptools.setup(
    name=ext_name,
    version=version,
    author="Jonathan B",
    author_email="jbloedow@idmod.org",
    description="IDM's Lightning Fast Next-Generation Agent-Based Modeling Prototype",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InstituteforDiseaseModeling/laser",
    #packages=setuptools.find_packages(exclude=['laser_sql_model/*']),
    packages=['laser_numpyc_model'],
    package_data={'laser_numpyc_model': ['makefile', 'eula_preproc.sh', 'requirements.txt']},
    entry_points={
        'console_scripts': [
            'laser_numpyc_model.bootstrap=laser_numpyc_model.bootstrap:main',
        ],
    },
    include_package_data=True,
    ext_modules=[numpyc],
    cmdclass={'build_ext': CustomBuildExt},
    setup_requires=['wheel'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
