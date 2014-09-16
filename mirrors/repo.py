import Queue
import logging
import threading
import time
import subprocess
import os
from datetime import datetime
from mirrors.libmirrors import t2s


class Singleton(type):
    """Singleton Class for RepoManager"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Repo:
    def __init__(self, name, config):
        """A repo object which stores info about a single repo.

        :param str name: Name of repo
        :param config: running config options
        :type config: ConfigParser.ConfigParser
        """

        # ConfigParser Object which all of the repo info is stored under the repo name
        self.config = config
        # Name of the Repo
        self.name = name

        # Singleton of RepoManager
        self.repo_manager = RepoManager()

        if not self.config.has_option(self.name, 'source'):
            raise self.RepoError("No Source Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'destination'):
            self.config.set(self.name, 'destination', './distro/')
        directory = os.path.dirname(self.config.get(self.name, 'destination'))
        if not os.path.exists(directory):
            logging.info("Creating {0}".format(directory))
            os.makedirs(directory)

        if not self.config.has_option(self.name, 'rsync_args'):
            raise self.RepoError("No rsync_args Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'weight'):
            self.config.set(self.name, 'weight', '0')

        if self.config.has_option(self.name, 'async_sleep') and self.config.has_option(self.name, 'hourly_sync'):
            raise self.repo_manager.RepoError("Both async_sleep and hourly_sync cannot be defined".format(self.name), self.name)
        elif not self.config.has_option(self.name, 'async_sleep') and not self.config.has_option(self.name, 'hourly_sync'):
            raise self.repo_manager.RepoError("Either async_sleep or hourly_sync must be defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'pre_command'):
            self.config.set(self.name, 'pre_command', '')

        if not self.config.has_option(self.name, 'post_command'):
            self.config.set(self.name, 'post_command', '')

        if not self.config.has_option(self.name, 'log_file'):
            self.config.set(self.name, 'log_file', './log/{0}.log'.format(self.name))
            logging.info("No log_file declared in {0}, defaulting to '{0}.log'".format(self.name))
            #raise self.RepoError("no log_file defined in {0}".format(self.name), self.name)

        log_file = self.config.get(self.name, "log_file")
        if os.path.isfile(self.config.get(self.name, "log_file")):
            try:
                open(log_file, 'r').close()
                logging.debug("{0} log file good for writing".format(self.name))
            except IOError:
                logging.error("Error opening {0} for writing".format(self.name))
        else:
            directory = os.path.dirname(log_file)
            if not os.path.exists(directory):
                logging.info("Creating {0}".format(directory))
                os.makedirs(directory)
            try:
                open(log_file, 'a').close()
            except IOError:
                logging.error("Error creating {0}".format(self.name))

        # Contains rsync_thread
        self.__sync = self.rsync_thread(self.name, self.config)

        # Status of Repo Queue
        self.queued = False

        logging.info("{0} loaded successfully".format(self.name))

    def is_alive(self):
        """Returns Bool of syncing status."""
        return bool(self.__sync.p)

    def running_time(self):
        """Return total running time of Sync.

        TODO
        """
        pass

    def sleep_time(self):
        """Return sleep duration.

        TODO
        """
        pass

    def time_remaining(self):
        """Return time left until sleep is over.

        TODO
        """
        pass

    def terminate(self):
        """Send SIGTERM to the rsync process."""
        if self.is_alive():
            self.__sync.p.terminate()

    def kill(self):
        """Send SIGKILL to the rsync process."""
        if self.is_alive():
            self.__sync.p.kill()

    def __rebuild(self):
        """Destroy and recreate the rsync object and settings.

        This will wipe all currently running rsync timers
        """
        del self.__sync
        self.__sync = self.rsync_thread(self.name, self.config)

    def start_sync(self):
        """Run an rsync against the repo source."""
        self.__rebuild()
        self.__sync.start()

    class rsync_thread(threading.Thread):
        """extended threading.Thread class to control rsync via subprocess
       
        :param str name: Name of repo
        :param config: running config options
        :type config: ConfigParser.ConfigParser
        """
        def __init__(self, name, config):
            threading.Thread.__init__(self)
            self.config = config
            self.p = None
            self.name = name

            # Singleton of RepoManager
            self.repo_manager = RepoManager()

            self.start_time = None
            self.finish_time = None
            self.thread_timer = None

            # Set thread to daemon
            self.daemon = True

        def run(self):
            logging.debug("Opening {0} for writing".format(self.config.get(self.name, 'log_file')))
            output_file = open(self.config.get(self.name, 'log_file'), 'a')

            logging.debug("Running rsync with {0} {1} {2}".format(
                self.config.get(self.name, "rsync_args"),
                self.config.get(self.name, "source"),
                self.config.get(self.name, "destination")))

            self.start_time = datetime.now()
            logging.info("Starting sync {0} at {1}".format(self.name, self.start_time))

            self.p = subprocess.Popen("rsync {0} {1} {2}".format(
                self.config.get(self.name, "rsync_args"),
                self.config.get(self.name, "source"),
                self.config.get(self.name, "destination")).split(),
                shell=False,
                stdout=output_file,
                stderr=subprocess.STDOUT)
            # Bock until the subprocess is done
            self.p.wait()

            if self.config.get(self.name, "post_command"):
                logging.debug("Running post_cmd {0}".format(self.config.get(self.name, "post_command")))
                self.post_cmd = subprocess.Popen("{0}".format(
                    self.config.get(self.name, "post_command")),
                    shell=True,
                    stdout=output_file,
                    stderr=subprocess.STDOUT)
                self.post_cmd.wait()
                logging.info("Done running post_command for {0}".format(self.name))

            ### Re-Queue the job
            t = t2s(self.config.get(self.name, "async_sleep"))
            self.thread_timer = threading.Timer(t, self.repo_manager.enqueue, [self.name])
            self.thread_timer.start()
            logging.info("{0} will sleep for {1}".format(self.name, self.config.get(self.name, "async_sleep")))

            # Clear out the current process when it finishes
            del self.p
            self.p = None

            self.finish_time = datetime.now()
            logging.info("Finished sync {0} at {1}".format(self.name, self.finish_time))

            logging.debug("Closing {0}".format(self.config.get(self.name, 'log_file')))
            output_file.close()


class RepoManager(object):
    __metaclass__ = Singleton

    def __init__(self, config):
        """Singleton manager of the Repositories and Threading.

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

        if not self.config.has_option('DEFAULT', 'check_sleep'):
            config.set("DEFAULT", 'check_sleep', '30')

        # Current Running Syncs: Compared against max set in config
        self.running_syncs = 0

        self.async_thread = threading.Thread(name="async_control", target=self.__check_queue)
        self.async_thread.daemon = True
        self.async_thread.start()

    def __check_queue(self):
        """Queue loop checker for async_control"""
        while(True):
            repo = self.repo_queue.get()[1]
            if self.running_syncs <= self.config.get("DEFAULT", "async_processes"):
                logging.debug("Acquired {0}".format(repo.name))
                repo.queued = False
                self.running_syncs += 1
                repo.start_sync()
            else:
                logging.debug("Re-queuing {0}, no open threads".format(repo.name))
                self.repo_queue.put([-11, repo])
                logging.debug("Sleeping for {0}".format(self.config.get("DEFAULT", "check_sleep")))
                time.sleep(float(self.config.get("DEFAULT", "check_sleep")))

    def repo(self, name):
        """Return Repo object if exists.

        :param name: Name of Repo to return
        :return Repo: Repo object if exists
        :return None: If no repo exists by that name
        """
        if name in self.repo_dict:
            return self.repo_dict[name]
    get_repo = repo

    def add_repo(self, name):
        """Create a Repo for a section in the running config.

        If the section does not exist will raise a Repo.RepoError
        :param str name: Name of repo
        """
        if self.config.has_section(name):
            repo = Repo(name, self.config)
            self.repo_dict[name] = repo
        else:
            raise self.RepoError("Cannot Create Repo, Section {0} does not exist".format(name))

    def del_repo(self, name):
        """Delete repo object from dict.

        :param str name: Name of repo
        :raises RepoError: if no repo exists by passed in name
        """
        if self.repo_dict[name]:
            del self.repo_dict[name]
        else:
            raise self.RepoError("Cannot Delete Repo, Repo {0} does not exist".format(name))

    def enqueue(self, name):
        """Add repo to the queue

        :param str name: Name of repo
        :return bool: True if successful or False if repo already queued
        """
        if not self.repo_dict[name].queued and not self.repo_dict[name].is_alive():
            self.repo_queue.put([self.config.get(name, "weight"), self.repo_dict[name]])
            self.repo_dict[name].queued = True
            return True
        else:
            return False

    class DefaultError(Exception):
        def __init__(self, message):
            """DEFAULT Config Error"""
            Exception.__init__(self, message)
            self.message = message

    class RepoError(Exception):
        def __init__(self, message, name):
            """Repo Config Error"""
            Exception.__init__(self, message)
            self.message = message
            self.name = name
