#!/usr/bin/env python
import argparse
import configparser
import subprocess
from librepo import repo

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.parse_args()


    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')

    testRepo = repo()
    testRepo.config_options = {'test':'test'}
    print(testRepo.config_options)
