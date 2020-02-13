# piescope

PIE-scope: integrated cryo-correlative light and FIB/SEM microscopy

This is the back end library supporting PIE-scope microscopy functions.
The front ebd GUI can be found at: https://github.com/DeMarcoLab/piescope_gui

You can read more about this instrument for correlative microscopy here:
https://doi.org/10.7554/eLife.45919.001

## Installation

See the detailed installation guide [INSTALLATION.md](INSTALLATION.md)

Install or upgrade to the latest version directly from GitHub with:
If you already have an installation and want to upgrade your version of
`piescope`, download the latest release wheel file (`.whl`) from:

https://github.com/DeMarcoLab/piescope/releases


```
pip install $NAME_OF_WHEEL_FILE.whl
```

## Runing the program

You can check what version you're currently using in python:

```
    import piescope
    piescope.__version__
```

This library is not generally intended for direct use,
instead it is expected it will be used as the back end functionality to
the `piescope_gui` library: https://github.com/DeMarcoLab/piescope_gui
