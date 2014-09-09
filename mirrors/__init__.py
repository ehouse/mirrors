#!/usr/bin/env python
import argparse
import ConfigParser
import logging
import os
from mirrors.repo import RepoManager
from mirrors.cmdline import Console


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", metavar="config", help="Configuration File Location", required=True)
    parser.add_argument("--log", metavar="logfile", help="Path to Log File")
    debug_group = parser.add_mutually_exclusive_group(required=False)
    debug_group.add_argument('-v', '--verbose', action='store_true', help="Increase Verbosity")
    debug_group.add_argument('-D', '--debug', action='store_true', help="Debug Mode")
    args = parser.parse_args()

    config = ConfigParser.ConfigParser()
    config.read(args.c)

    if args.log:
        log_file = args.log
    elif config.has_option("DEFAULT", "log_file"):
        log_file = config.get("DEFAULT", "log_file")
    else:
        log_file = ""

    directory = os.path.dirname(config.get("DEFAULT", 'log_file'))
    if not os.path.exists(directory):
        logging.info("Creating {0}".format(directory))
        os.makedirs(directory)
        open(config.get("DEFAULT","log_file"), 'a').close()

    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s', filename=log_file)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s, %(threadName)s, %(levelname)s: %(message)s', filename=log_file)
        logging.debug("Turning Debug On")

    logging.debug("Beginning Loading Repos")
    try:
        manager = RepoManager(config)
    except RepoManager.DefaultError as e:
        logging.critical("Critical Failure While Loading DEFAULT Section | {0}".format(e.message))
        logging.critical("Program Terminating Due to Critical Error")
        exit(0)

    for name in config.sections():
        try:
            manager.add_repo(name)
            ### TODO: Make this optional
            manager.enqueue(name)
        except RepoManager.RepoError as e:
            logging.warning("FAILED TO LOAD {0} | {1}".format(e.name, e.message))
    logging.debug("Finished Loading Repos")

    logging.debug("Starting Command Loop")
    console = Console(manager)
    console.cmdloop()
