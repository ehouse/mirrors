#!/usr/bin/env python
import argparse
import ConfigParser
import subprocess
import logging
from mirrors.librepo import repo
from mirrors.librepo import repoManager

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", metavar="config", help="Configuration File Location", required=True)
    parser.add_argument("--log", metavar="logfile", help="Path to Log File")
    debugGroup = parser.add_mutually_exclusive_group(required=False)
    debugGroup.add_argument('-v', '--verbose', action='store_true',help="Increase Verbosity")
    debugGroup.add_argument('-D', '--debug', action='store_true',help="Debug Mode")
    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(args.c)

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s', filename=args.log)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s', filename=args.log)
        logging.debug("Turning Debug On")

    logging.debug("Begining Loading Repos")
    manager = repoManager()
    for name in config.sections():
        try:
            manager.repoList.append(repo(name, config))
        except repo.RepoError as e:
            logging.warning("FAILED TO LOAD {0} | {1}".format(e.name, e.message))
    logging.debug("Finished Loading Repos")
