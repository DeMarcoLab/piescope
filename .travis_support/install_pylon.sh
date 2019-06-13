#!/bin/bash

# Config for Basler Pylon software suite
# https://www.baslerweb.com/en/sales-support/downloads/software-downloads/
export PYTHON_VERSION="36"
export PYLON_VERSION="5.2.0"
export PYLON_MD5="fe9831729afeaf91005e93abc5e51d5b"
export PYLON_INSTALLER="${HOME}/pylon.tar.gz"
export PYLON_DIR="${HOME}/pylon-5.2.0.13457-x86_64"
export PYLON_URL="https://www.baslerweb.com/fp-1551786516/media/downloads/software/pylon_software/pylon-${PYLON_VERSION}.13457-x86_64.tar.gz"
# Python pypylon library (install after the pylon software suite)
# https://github.com/basler/pypylon/releases
export PYPYLON_VERSION="1.4.0"
export PYPYLON_MD5="aa47574b0067b7404568a0b17b7abd47"
export PYPYLON_WHEEL="${HOME}/pypylon-${PYPYLON_VERSION}-cp${PYTHON_VERSION}-cp${PYTHON_VERSION}m-linux_x86_64.whl"
export PYPYLON_URL="https://github.com/basler/pypylon/releases/download/${PYPYLON_VERSION}/pypylon-${PYPYLON_VERSION}-cp${PYTHON_VERSION}-cp${PYTHON_VERSION}m-linux_x86_64.whl"

# Install the Basler Pylon software.
curl -L "${PYLON_URL}" > "${PYLON_INSTALLER}"
openssl md5 "${PYLON_INSTALLER}" | grep "${PYLON_MD5}"
tar -xvzf "${PYLON_INSTALLER}"
tar -C /opt -xzf */pylonSDK*.tar.gz
yes | ./*/setup-usb.sh

# Install the python pypylon package
curl -L "${PYPYLON_URL}" > "${PYPYLON_WHEEL}"
openssl md5 "${PYPYLON_WHEEL}" | grep "${PYPYLON_MD5}"
pip install "${PYPYLON_WHEEL}"
