import Queue
import logging
import threading
import time
import subprocess
import os
from datetime import datetime
from mirrors.libmirrors import t2s


class Singleton(type):
    """Singleton Class for RepoManager."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Repo(object):
    def __init__(self, name, config):
        """A repo object which stores info about a single repo.

        :param str name: Name of repo.
        :param config: running config options.
        :type config: ConfigParser.ConfigParser
        """

        # ConfigParser Object which all of the repo info is stored under the repo name
        self.config = config
        # Name of the Repo
        self.name = name

        # deactive repos will not run
        self.deactive = False

        # Status of Repo Queue
        self.queued = False

        # Singleton of RepoManager
        self.repo_manager = RepoManager()

        # Contains rsync_thread
        self.__sync = self.rsync_thread(self.name, self.config)

        # Config Validation Section
        if not self.config.has_option(self.name, 'source'):
            raise RepoConfigError("No Source Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'destination'):
            self.config.set(self.name, 'destination', './distro/')
        directory = os.path.dirname(self.config.get(self.name, 'destination'))
        if not os.path.exists(directory):
            logging.info("Creating {0}".format(directory))
            os.makedirs(directory)

        if not self.config.has_option(self.name, 'rsync_args'):
            raise RepoConfigError("No rsync_args Defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'weight'):
            self.config.set(self.name, 'weight', '0')

        if not self.config.has_option(self.name, 'deactive'):
            self.deactive = self.config.getboolean(self.name, 'deactive')
        else:
            self.config.set(self.name, 'deactive', 'False')

        if self.config.has_option(self.name, 'async_sleep') and self.config.has_option(self.name, 'hourly_sync'):
            raise RepoConfigError("Both async_sleep and hourly_sync cannot be defined".format(self.name), self.name)
        elif not self.config.has_option(self.name, 'async_sleep') and not self.config.has_option(self.name, 'hourly_sync'):
            raise RepoConfigError("Either async_sleep or hourly_sync must be defined".format(self.name), self.name)

        if not self.config.has_option(self.name, 'pre_command'):
            self.config.set(self.name, 'pre_command', '')

        if not self.config.has_option(self.name, 'post_command'):
            self.config.set(self.name, 'post_command', '')

        if not self.config.has_option(self.name, 'log_file'):
            self.config.set(self.name, 'log_file', './log/{0}.log'.format(self.name))
            logging.info("No log_file declared in {0}, defaulting to '{0}.log'".format(self.name))
        # end config validation section

        log_file = self.config.get(self.name, "log_file")
        directory = os.path.dirname(log_file)
        if not os.path.exists(directory):
            logging.info("Creating {0}".format(directory))
            try:
                os.makedirs(directory)
            except IOError:
                logging.error("Failed to create {0}".format(directory))
        try:
            open(log_file, 'a').close()
            logging.debug("{0} log file good for writing".format(self.name))
        except IOError:
            logging.error("Error opening {0} for writing".format(self.name))

        if(self.deactive):
            logging.info("{0} loaded successfully, but deactive".format(self.name))
        else:
            logging.info("{0} loaded successfully".format(self.name))

    def is_alive(self):
        """Bool of syncing status."""
        return bool(self.__sync.p)

    def running_time(self):
        """Total running time of active sync.

        :returns: int -- total syncing time of sync or 0 if not syncing.
        """
        pass

    def sleep_time(self):
        """Sleep duration of sleeping sync.

        :returns: int -- sleep duration time or 0 if not sleeping.
        """
        pass

    def time_remaining(self):
        """Return time left until sleep is over.

        TODO
        """
        pass

    def terminate(self):
        """Send SIGTERM To the rsync process."""
        if self.is_alive():
            logging.info("Terminating {0}".format(self.name))
            self.__sync.p.terminate()

    def kill(self):
        """Send SIGKILL To the rsync process."""
        if self.is_alive():
            logging.info("KIlling {0}".format(self.name))
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
        """Extended threading.Thread class to control rsync via subprocess.

        :param str name: Name of repo.
        :param config: Running config options.
        :type config: Configparser.Configparser
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
            # bock until the subprocess is done
            self.p.wait()

            if self.config.get(self.name, "post_command"):
                logging.debug("running post_cmd {0}".format(self.config.get(self.name, "post_command")))
                self.post_cmd = subprocess.Popen("{0}".format(
                    self.config.get(self.name, "post_command")),
                    shell=True,
                    stdout=output_file,
                    stderr=subprocess.STDOUT)
                self.post_cmd.wait()
                logging.info("Done running post_command for {0}".format(self.name))

            t = t2s(self.config.get(self.name, "async_sleep"))
            self.thread_timer = threading.Timer(t, self.repo_manager.enqueue, [self.name])
            self.thread_timer.start()
            logging.info("{0} will sleep for {1}".format(self.name, self.config.get(self.name, "async_sleep")))

            # clear out the current process when it finishes
            del self.p
            self.p = None

            self.finish_time = datetime.now()
            logging.info("finished sync {0} at {1}".format(self.name, self.finish_time))

            logging.debug("closing {0}".format(self.config.get(self.name, 'log_file')))
            output_file.close()


class RepoManager(object):
    __metaclass__ = Singleton

    def __init__(self, config):
        """Singleton manager of the repositories and threading.

        :param config: Running config options.
        :type config: Configparser.Configparser
        """
        # configparser object which all of the repomanager configs are stored under the GLOBAL Section
        self.config = config

        # priority queue for async processing
        self.repo_queue = Queue.PriorityQueue(0)
        # list of repo objects
        self._repo_dict = dict()

        if not self.config.has_section("GLOBAL"):
            raise GlobalError("Config requires GLOBAL Section")

        if not self.config.has_option('GLOBAL', 'async_processes'):
            raise GlobalError("No async_processes value defined in GLOBAL")

        if not self.config.has_option('GLOBAL', 'check_sleep'):
            config.set("GLOBAL", 'check_sleep', '30')

        # current running syncs: compared against max set in config
        self.running_syncs = 0

        self.async_thread = threading.Thread(name="async_control", target=self.__check_queue)
        self.async_thread.daemon = True
        self.async_thread.start()

    def __check_queue(self):
        """Queue loop checker for async_control."""
        while(True):
            # Check for deactive repos
            found = None

            while not found:
                repo = self.repo_queue.get()[1]
                if not repo.deactive:
                    found = True
                else:
                    # If deactive, toss aside
                    break

            if self.running_syncs <= self.config.get("GLOBAL", "async_processes"):
                logging.debug("Acquired {0}".format(repo.name))
                repo.queued = False
                self.running_syncs += 1
                repo.start_sync()
            else:
                logging.debug("Requeuing {0}, no open threads".format(repo.name))
                self.repo_queue.put([-11, repo])
                time.sleep(30)

    def get_repo(self, name):
        """Return repo object if exists.

        :param str name: name of repo.
        :returns: Repo Object.
        :rtype: Repo
        :returns: None -- if no repo exists by that name.
        """
        if name in self._repo_dict:
            return self._repo_dict[name]

    def gen_repo(self):
        """Generator for repo_dict.

        :returns: Repo Object
        :rtype: Repo
        """
        for name in self._repo_dict:
            yield self._repo_dict[name]

    def add_repo(self, name):
        """Create a repo for a section in the running config.

        :param str name: Name of repo.
        :raises Repo.RepoConfigError: if no config exists for given repo name.
        """
        if self.get_repo(name):
            raise RepoConfigError("Cannon create repo {0}, already created".format(name), name)

        if self.config.has_section(name):
            repo = Repo(name, self.config)
            self._repo_dict[name] = repo
        else:
            raise RepoConfigError("Cannot create repo, section {0} does not exist".format(name), name)

    def deactivate(self, name):
        """Deactivate repo from syncing.

        :param str name: Name of repo.
        :raises Repo.RepoError: if no repo exists by given name.
        """
        if self.get_repo(name):
            if self.get_repo(name).deactive:
                # nothing to do, already deactive
                return
            self.get_repo(name).deactive = True
            logging.info("Deactivating {0}".format(name))
        else:
            raise RepoError("No Repo Named {0}".format(name), name)

    def activate(self, name):
        """Activate repo for syncing.

        :param str name: Name of Repo.
        :raises Repo.RepoError: if no repo exists by given name.
        """
        if self.get_repo(name):
            if not self.get_repo(name).deactive:
                # nothing to do, already active
                return
            self.get_repo(name).deactive = False
            self.enqueue(name)
            logging.info("Activating {0}".format(name))
        else:
            raise RepoError("No Repo Named {0}".format(name), name)

    def status(self, name):
        """Return status of Repo.

        :param str name: Name of Repo.
        :returns: str -- Status of Repo
        """
        if not self.get_repo(name):
            raise RepoError("Repo {0} doesn't exist".format(name), name)

        if self.get_repo(name).deactive:
            return "{0} is deactive".format(name)
        elif self.get_repo(name).queued:
            return "{0} is queued".format(name)
        elif self.get_repo(name).is_alive():
            return "{0} is syncing".format(name)
        else:
            return "{0} is sleeping".format(name)

    def del_repo(self, name):
        """Delete repo object from dict.

        :param str name: Name of repo.
        :raises Repo.RepoError: if no repo exists by passed in name.
        """
        if self.get_repo(name):
            del self._repo_dict[name]
        else:
            raise RepoError("Cannot delete repo, repo {0} does not exist".format(name))

    def enqueue(self, name):
        """Add repo to the queue.

        :param str name: Name of repo.
        :raises Repo.RepoError: if repo is already queued or doesn't exist.
        """
        if not self.get_repo(name):
            raise RepoError("Repo {0} doesn't exist".format(name), name)

        if self.get_repo(name).deactive:
            raise RepoError("Failed to queue repo, {0} is deactive.".format(name), name)

        if self.get_repo(name).queued:
            raise RepoError("Failed to queue repo, {0} already queued.".format(name), name)

        if self.get_repo(name).is_alive():
            raise RepoError("Failed to queue Repo, {0} is syncing.".format(name), name)

        self.repo_queue.put([self.config.get(name, "weight"), self.get_repo(name)])
        self.get_repo(name).queued = True


class GlobalError(Exception):
    def __init__(self, message):
        """Fatal GLOBAL Section Config Error."""
        Exception.__init__(self, message)
        self.message = message


class RepoConfigError(Exception):
    def __init__(self, message, name):
        """Non-Fatal Repo config Error."""
        Exception.__init__(self, message)
        self.message = message
        self.name = name


class RepoError(Exception):
    def __init__(self, message, name):
        """Non-Fatal Repo Error."""
        Exception.__init__(self, message)
        self.message = message
        self.name = name
