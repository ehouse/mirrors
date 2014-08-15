import Queue
import logging
import threading
import time
import subprocess
import os
from mirrors.libmirrors import t2s


class Repo:
    def __init__(self, name, config):
        """A repo object which stores info about a single repo.

        Stores most configuration within the config object. All
        of the work is done by the RepoManager Class
        :param name: string name of repo
        :param config: running config options
        :type config: ConfigParser.ConfigParser
        """

        # ConfigParser Object which all of the repo info is stored under the repo name
        self.config = config
        # Name of the Repo
        self.name = name

        if not self.config.has_option(self.name, 'source'):
            raise self.RepoError("No Source Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'destination'):
            config.set(self.name, 'destination', './distro/')
        directory = os.path.dirname(config.get(self.name, 'destination'))
        if not os.path.exists(directory):
            logging.info("Creating {0}".format(directory))
            os.makedirs(directory)

        if not self.config.has_option(self.name, 'rsync_args'):
            raise self.RepoError("No rsync_args Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'weight'):
            config.set(self.name, 'weight', '0')

        if self.config.has_option(self.name, 'async_sleep') and self.config.has_option(self.name, 'hourly_sync'):
            raise self.RepoError("Both async_sleep and hourly_sync cannot be defined".format(self.name), self.name)
        elif not self.config.has_option(self.name, 'async_sleep') and not self.config.has_option(self.name, 'hourly_sync'):
            raise self.RepoError("Either async_sleep or hourly_sync must be defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'pre_command'):
            config.set(self.name, 'pre_command', '')

        if not self.config.has_option(self.name, 'post_command'):
            config.set(self.name, 'post_command', '')

        if not self.config.has_option(self.name, 'log_file'):
            # config.set(self.name, 'log_file', './log/{0}'.format(self.name))
            raise self.RepoError("no log_file defined in {0}".format(self.name), self.name)

        directory = os.path.dirname(config.get(self.name, 'log_file'))
        if not os.path.exists(directory):
            logging.info("Creating {0}".format(directory))
            os.makedirs(directory)
        open(config.get(self.name, 'log_file'), 'a').close()

        # Contains rsync_thread
        self.__running_sync = None

        # Status of Repo Queue
        self._queued = False

        logging.info("{0} loaded succesfully".format(self.name))

    def terminate(self):
        """Send SIGTERM to the rsync process"""
        if self.__running_sync:
            self.__running_sync.terminate()

    def kill(self):
        """Send SIGKILL to the rsync process"""
        if self.__running_sync:
            self.__running_sync.kill()

    def is_alive(self):
        """Returns Bool of syncing status"""
        if self.__running_sync:
            return self.__running_sync.is_alive()
        return False

    def is_queued(self):
        """Returns Bool of queued status"""
        return self._queued

    def rsync(self):
        """Run an rsync against the repo source"""
        self.__running_sync = self.rsync_thread(self.name, self.config)
        self.__running_sync.start()

    class rsync_thread(threading.Thread):
        def __init__(self, name, config):
            threading.Thread.__init__(self)

            self.config = config

            self.p = None

            self.name = name

        def run(self):
            logging.debug("Running Sync for {0}".format(self.name))

            output_file = open(self.config.get(self.name, 'log_file'), 'w')
            logging.debug(self.config.get(self.name, 'log_file'))

            logging.debug("Running rsync {0} {1} {2}".format(
                self.config.get(self.name, "rsync_args"),
                self.config.get(self.name, "source"),
                self.config.get(self.name, "destination")).split())

            self.p = subprocess.Popen("rsync {0} {1} {2}".format(
                self.config.get(self.name, "rsync_args"),
                self.config.get(self.name, "source"),
                self.config.get(self.name, "destination")).split(),
                shell=False,
                stdout=output_file,
                stderr=subprocess.STDOUT)

            logging.debug("Finished Sync for {0}".format(self.name))

            output_file.close()

        def terminate(self):
            """Send SIGTERM to the child rsync process"""
            if not self.p.poll():
                self.p.terminate()

        def kill(self):
            """Send SIGKILL to the child rsync process"""
            if not self.p.poll():
                self.p.kill()

        def is_alive(self):
            """Return Bool of alive status"""
            return not bool(self.p.poll())


class RepoManager:
    def __init__(self, config):
        """Manager of the Repositories and Threading.

        Controls when and what gets run
        :param config: running config options
        :type config: ConfigParser.ConfigParser
        """
        # ConfigParser Object which all of the RepoManager configs are stored under the DEFAULT section
        self.config = config

        # Priority Queue for async processing
        self.repo_queue = Queue.PriorityQueue(0)
        # List of Repo Objects
        self.repo_dict = dict()

        if not self.config.defaults():
            raise self.DefaultError("Config Requires DEFAULT Section")

        if not self.config.has_option('DEFAULT', 'async_processes'):
            raise self.DefaultError("No async_processes value defined in DEFAULT")

        self.async_thread = threading.Thread(name="async_control", target=self.__check_queue)
        self.async_thread.daemon = True
        self.async_thread.start()

    def __check_queue(self):
        """Queue loop checker for async_control"""
        while(True):
            logging.debug("Blocking on Priority Queue")
            repo = self.repo_queue.get()
            logging.debug("Done Blocking on Priority Queue | Aquired {0}".format(repo.name))
            repo.rsync()

    def repo(self, name):
        """Return Repo object if exists.

        :param name: Name of Repo to return
        :return Repo: Repo object if exists
        :return None: If no repo exists by the pass in name
        """
        if name in self.repo_dict:
            return self.repo_dict[name]
    get_repo = repo

    def add_repo(self, name):
        """Create a Repo for a section in the running config.

        If the section does not exist will raise a Repo.RepoError
        :param name: string of a repo section in the config
        """
        if self.config.has_section(name):
            repo = Repo(name, self.config)
            self.repo_dict[name] = repo
        else:
            raise self.RepoError("Cannot Create Repo, Section {0} does not exist".format(name))

    def enqueue(self, name):
        """Add repo to the queue

        :param name: string of a repo section in the config
        :return Bool: True if successful or False if repo already queued
        """
        if not self.repo_dict[name].is_queued():
            self.repo_queue.put(self.repo_dict[name])
            self.repo_dict[name]._queued = True
            return True
        else:
            return False

    class DefaultError(Exception):
        def __init__(self, message):
            """DEFAULT Section Config Error"""
            Exception.__init__(self, message)
            self.message = message

    class RepoError(Exception):
        def __init__(self, message, name):
            """Repo Config Error"""
            Exception.__init__(self, message)
            self.message = message
            self.name = name
