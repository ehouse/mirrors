#!/usr/bin/env python
import argparse
import configparser
import subprocess
from librepo import repo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-c", "--config", help="path to config file")
    parser.parse_args()
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.sections()
    config.read(args.config)

    print(config._sections)
    for key in config._sections:
        print(config._sections[key])
