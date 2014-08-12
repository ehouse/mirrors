import Queue
import logging
import threading
import time
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
            logging.info("Destination not set for {0}. Using Default (./distro/)".format(self.name))
            config.set(self.name, 'destination', './distro/')

        if not self.config.has_option(self.name, 'rsync_args'):
            raise self.RepoError("No rsync_args Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'weight'):
            logging.info("weight not set for {0}. Using Default (0)".format(self.name))
            config.set(self.name, 'weight', '0')

        if self.config.has_option(self.name, 'async_sleep') and self.config.has_option(self.name, 'hourly_sync'):
            raise self.RepoError("Both async_sleep and hourly_sync cannot be defined".format(self.name), self.name)
        elif not self.config.has_option(self.name, 'async_sleep') and not self.config.has_option(self.name, 'hourly_sync'):
            raise self.RepoError("Either async_sleep or hourly_sync must be defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'pre_command'):
            logging.info("pre_command not set for {0}. Leaving blank".format(self.name))
            config.set(self.name, 'pre_command', '')

        if not self.config.has_option(self.name, 'post_command'):
            logging.info("post_command not set for {0}. Leaving blank".format(self.name))
            config.set(self.name, 'post_command', '')

        # Start time of last sucessful run
        self.last_run = None
        # Time of last run
        self.last_run_length = None
        # Repo Avg run time
        self.run_avg = None

        logging.info("{0} loaded succesfully".format(self.name))

    def returnConfig(self):
        """Returns running config.

        :return dict: Dict of running config
        """
        return self.config._sections[self.name]

    def rsync(self):
        """Run an rsync against the repo source"""
        logging.debug("Running A sync".format(self.name))

    class RepoError(Exception):
        def __init__(self, message, name):
            """Repo Config Error"""
            self.message = message
            self.name = name
            Exception.__init__(self, message)


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
        self.repo_list = []
        # List of Thread Objects
        self.thread_pool = []

        if not self.config.defaults():
            raise self.DefaultError("Config Requires DEFAULT Section")

        if not self.config.has_option('DEFAULT', 'threads'):
            raise self.DefaultError("No threads value defined in DEFAULT")

        if not self.config.has_option('DEFAULT', 'check_sleep'):
            raise self.DefaultError("No check_sleep value defined in DEFAULT")

        for i in range(int(self.config.get("DEFAULT","threads"))):
            t = threading.Thread(name="async_{0}".format(i), target=self.__check_queue)
            t.start()
            self.thread_pool.append(t)

    def __check_queue(self):
        while(True):
            logging.debug("Blocking on Priority Queue")
            repo = self.repo_queue.get()
            logging.debug("Done Blocking on Priority Queue | Aquired {0}".format(repo.name))
            repo.rsync()
            logging.debug("Sleep for 30")
            time.sleep(30)

    class DefaultError(Exception):
        def __init__(self, message):
            """DEFAULT Section Config Error"""
            self.message = message
            Exception.__init__(self, message)
