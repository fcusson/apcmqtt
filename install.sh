#!/bin/bash

function _main() {
    # check for dependencies
    install_dependencies

    # build module
    #TODO

    # create start file
    #TODO

    # copy service file
    #TODO
    :
}

function install_dependencies() {

    if [ -x "$(command -v apt)" ]; then
        apt install -y apcupsd
    elif [ -x "$(command -v dnf)" ]; then
        dnf install -y apcupsd
    elif [ -x "$(command -v zypper)" ]; then
        zypper addrepo https://download.opensuse.org/repositories/openSUSE:Factory/standard/openSUSE:Factory.repo
        zypper refresh
        zypper -n install apcupsd
    elif [ -x "$(command -v pacman)" ]; then
        yes | pacman -S apcupsd
    elif [ -x "$(command -v emerge)" ]; then
        emerge sync && emerge -y apcupsd
    elif [ -x "$(command -v apk)" ]; then
        apk add apcupsd
    fi

    pip install paho-mqtt

}
