# Software Installation Guide

## Dependencies

Hardware requirements
* FIB/SEM microscope (a commercial product by ThermoFisher FEI)
* Basler detector (https://www.baslerweb.com)
* Toptica lasers (for the fluorescence microscope)
* SMARACT stage (controlling the fluorescence objective lens position)

Software requirements
* Python 3.6
* Autoscript software (a commercial product by ThermoFisher FEI)
* The Basler Pylon Software Suite (https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/)
* The Basler `pypylon` python package (https://github.com/basler/pypylon)

## Install the software pre-requisites
### Python
Python 3.6 is required.
The [Anaconda distribution](https://www.anaconda.com/distribution/)
is recommended.

It is also highly recommended to use virtual environments for development,
see [Managing Conda Environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
for more information.
(Optionally, you could use `virtualenv` if you prefer.)

Run these commands in your terminal to create a new virtual environment called `piescope`:
```
conda create -n piescope python=3.6 pip
conda activate piescope
```

### Installing Autoscript
Autoscript provides an API (application programming interface) for scripting
control of compatible FEI microscope systems.
This is a commercial product by Thermo Fisher FEI, please visit their website
at https://fei.com for information on pricing and installation.

We use Autoscript version 4.2.2

The version numbers of the python packages autoscript installs were:
* autoscript-core 5.1.0
* autoscript-sdb-microscope-client 4.2.2
* autoscript-sdb-microscope-client-tests 4.2.2
* autoscript-toolkit 4.2.2
* thermoscientific-logging 5.1.0

#### Add the autoscript python packages to your `site-packages`
You may find that the default AutoScript installation came bundled with a copy of Python 3.5, instead of the newer Python 3.6 this project requires.

If that is the case, you can copy the relevant python autoscript packages into the `site-packages` of your own python 3.6 environment. See [Managing Conda Environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for more information.

To add the AutoScript python packages to your new conda environment, follow these three steps:

1. Find the python environment that was created with your AutoScript installation.
Typically, you can expect the environment is named 'Autoscript', and its installed packages should be found at:
`C:\Program Files\Python35\envs\AutoScript\Lib\site-packages\`

***Troubleshooting:** If you're having trouble finding the location AutoScript chose to install its python packages into,*
*you can open the *default terminal* on your machine (eg: `cmd` for Windows) and type `where python` (Windows) or `which python` (Unix).*
*The result will be something like `C:\Program Files\Python35\envs\AutoScript\python.exe`.*
*Navigate to the environment location (in the example here, that's `C:\Program Files\Python35\envs\AutoScript\` *
*then change directories into `Lib`, and then the `site-packages` directory. This is where the python packages live.*

2. Find the conda environment location you just made called `autolamella-dev`.
`...conda/envs/autolamella-dev/Lib/site-packages/`

***Troubleshooting:** If you're having trouble finding the conda environment location for `autolamella-dev`*
*you can open the *Anaconda terminal* on your machine and type `where python` (Windows) or `which python` (Unix).*
*The result will be something like `C:\Users\yourusername\.conda\envs\autolamella-dev\python.exe`*
*Navigate to the environment location (in the example here, that's `C:\Users\yourusername\.conda\envs\autolamella-dev\` *
*then change directories into `Lib`, and then the `site-packages` directory.*
*This is where you want to add copies of the AutoScript python packages.*

3. Make a copy of the relevant AutoScript python packages into the conda environment.
You will need to copy:

* autoscript_core
* autoscript_core-5.4.1.dist-info
* autoscript_sdb_microscope_client
* autoscript_sdb_microscope_client_tests
* autoscript_sdb_microscope_client_tests-4.2.2.dist-info
* autoscript_sdb_microscope_client-4.2.2.dist-info
* autoscript_toolkit
* autoscript_toolkit-4.2.2.dist-info
* thermoscientific_logging
* thermoscientific_logging-5.4.1.dist-info


#### Check the AutoScript python packages work in your environment
You can check that this has worked by opening the *Anaconda terminal*, then typing:

```
conda activate autolamella-dev
python
```

And then at the python prompt:

```python
from autoscript_sdb_microscope_client import SdbMicroscopeClient
microscope = SdbMicroscopeClient()
```

If there is no `ImportError` raised, then you have been sucessful.

### Install the Pylon Software Suite and pypylon python library

#### Install the Pylon software suite
The Pylon software suite is produced by Basler for use with their detectors.
Instructions for downloading and installing the latest version of Pylon can be found on their website:
https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/

#### Install the pypylon python package
Basler also provide a Python API for use with their detectors and the Pylon software suite.
Instructions for downloading and installing the latest version can be found at:
https://github.com/basler/pypylon

## Install `piescope`
Download the latest `piescope` release wheel from https://github.com/DeMarcoLab/piescope/releases

Pip install the wheel file (`.whl`) into your python environment.
```
pip install $PIESCOPE_WHEEL_FILENAME.whl
```

### Python package dependencies
All the python package dependencies you need should be installed automatically,
with the exceptions already mentioned:
 1. Autoscript which is a commercial product and requires a special license key.
 2. The Basler `pypylon` python pacakge, made freely available at
 https://github.com/basler/pypylon

If you do encounter an issue with missing package dependencies,
you can always try reinstalling them with:
```
pip install -r requirements.txt
```

## Having problems?
* Check to see if Autoscript is correctly installed and configured.
* Check to see if your python environment contains all packages listed in
the requirements.txt
* Check that when you call python from the terminal, you get the python
environment containing the dependencies listed above
(i.e. you are not using a different python environment)
* Try cloning the repository and running the unit tests,
you may want to try installing from the source code.
