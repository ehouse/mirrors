import Queue
import ConfigParser
import logging

class Repo:
    def __init__(self, name, config):
        """
        Repository Object.
        Gets stored in RepoManager
        :param name: string name of repo
        :param config: running config options
        :type config: ConfigParser.ConfigParser
        """

        # running config options
        self.config = config

        ### Config Settings
        self.name = name

        if not self.config.has_option(self.name,'source'):
            raise self.RepoError("No Source Defined".format(self.name), self.name)

        if not self.config.has_option(self.name,'destination'):
            # destination not set, setting to default 
            config.set(self.name, 'destination', './dist/')

        if not self.config.has_option(self.name,'rsync_args'):
            raise self.RepoError("No rsync_args Defined".format(self.name), self.name)

        if not self.config.has_option(self.name,'weight'):
            # weight not set, setting to default 
            config.set(self.name, 'weight', '0')

        if self.config.has_option(self.name,'finish_offset') and self.config.has_option(self.name,'hourly_run'):
            raise self.RepoError("Both finish_offset and hourly_run cannot be defined".format(self.name), self.name)
        elif not self.config.has_option(self.name,'finish_offset') and not self.config.has_option(self.name,'hourly_run'):
            raise self.RepoError("Either finish_offset or hourly_run must be defined".format(self.name), self.name)

        if not self.config.has_option(self.name,'pre_command'):
            # weight not set, setting to default 
            config.set(self.name, 'pre_command', '')

        if not self.config.has_option(self.name,'post_command'):
            # weight not set, setting to default 
            config.set(self.name, 'post_command', '')

        ### Job Stats
        # Start time of last sucessful run
        self.last_run = None
        # Length of last run
        self.last_run_length = None
        # Repo Avg run length
        self.run_avg = None

        logging.info("{0} loaded succesfully".format(self.name))

    def returnConfig(self):
        """
        Returns running config.
        :return dict: Dict of running config
        """
        return self.config._sections[self.name]

    class RepoError(Exception):
        def __init__(self,message,name):
            self.message = message
            self.name = name
            Exception.__init__(self, message)


class RepoManager:
    def __init__(self):
        """
        Contains all Repository objects.
        Controls when and what gets run
        """
        self.repo_queue = Queue.PriorityQueue(0)
        self.repo_list = []
