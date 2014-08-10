#!/usr/bin/env python
import argparse
import ConfigParser
import subprocess
import logging
from mirrors.librepo import Repo, RepoManager

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", metavar="config", help="Configuration File Location", required=True)
    parser.add_argument("--log", metavar="logfile", help="Path to Log File")
    debug_group = parser.add_mutually_exclusive_group(required=False)
    debug_group.add_argument('-v', '--verbose', action='store_true',help="Increase Verbosity")
    debug_group.add_argument('-D', '--debug', action='store_true',help="Debug Mode")
    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(args.c)

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s', filename=args.log)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(levelname)s: %(message)s', filename=args.log)
        logging.debug("Turning Debug On")

    logging.debug("Begining Loading Repos")
    manager = RepoManager()
    for name in config.sections():
        try:
            manager.repoList.append(Repo(name, config))
        except Repo.RepoError as e:
            logging.warning("FAILED TO LOAD {0} | {1}".format(e.name, e.message))
    logging.debug("Finished Loading Repos")
