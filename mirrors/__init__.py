#!/usr/bin/env python
import argparse
import configparser
import subprocess
from mirrors.librepo import repo
from mirrors.librepo import repoManager

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
            action="store_true")
    parser.add_argument("-c", "--config", help="path to config file",)
    parser.parse_args()
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.sections()
    config.read(args.config)

    manager = repoManager()
    for key in config._sections:
        manager.repoList.append(repo(key, config._sections[key]))
