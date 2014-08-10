import Queue

class repo:
    def __init__(self, name, config):
        """
        Repository Object.
        Gets stored in RepoManager
        :param name: string name of repo
        :param config: dict of configuration
        """
        # running config options
        self._configOptions = config

        ### Config Settings
        # Repo Name
        self.name = name

        # rsync source url
        if('source' in self._configOptions):
            self.source = self._configOptions['source']
        else:
            raise ValueError('Config Sytax Error, Source Required in {0}.'.format(self.name),)

        # rsync args
        if('rsync_args' in self._configOptions):
            self.args = self._configOptions['rsync_args']
        else:
            raise ValueError('Config Sytax Error, rsync Args Required in {0}.'.format(self.name),)

        # rsync file destination
        if('destination' in self._configOptions):
            self.destination = self._configOptions['destination']
        else:
            self.destination = "./dist/"

        # Priority Queue Weight, value between -10 and 10
        if('weight' in self._configOptions):
            self.weight = self._configOptions['weight']
        else:
            self.weight = 0

        # Delay before next run is aloud to start
        if('finish_offset' in self._configOptions):
            self.delayTime = self._configOptions['finish_offset']
            self.strictTime = None
        # list of hours sync must happen on
        elif('hourly_run' in self._configOptions):
            self.strictTime = self._configOptions['hourly_run']
            self.delayTime = None
        else:
            raise ValueError('Config Sytax Error, either finish_offset or hourly_run required in {0}'.format(self.name))

        # Pre-bash Script
        if('pre_command' in self._configOptions):
            self.preScript = self._configOptions['pre_command']
        else:
            self.preScript = None

        # Post-Bash Script
        if('post_command' in self._configOptions):
            self.postScript = self._configOptions['post_command']
        else:
            self.postScript = None

        ### Job Stats
        # Start time of last sucessful run
        self.lastRun = None
        # Length of last run
        self.lastRunLength = None
        # Repo Avg run length
        self.runAvg = None

        ### Function Calls
        self.__writeConfig()

    def __writeConfig(self):
        """
        Writes running config to stored config.
        Required before syncing to disk
        """
        if self.source:
            self._configOptions['source'] = self.source
        if self.args:
            self._configOptions['rsync_args'] = self.args
        if self.destination:
            self._configOptions['destination'] = self.destination
        if self.weight:
            self._configOptions['weight'] = self.weight
        if self.delayTime:
            self._configOptions['finish_offset'] = self.delayTime
        if self.strictTime:
            self._configOptions['hourly_run'] = self.strictTime
        if self.preScript:
            self._configOptions['pre_command'] = self.preScripa
        else:
            self._configOptions['pre_command'] = None
        if self.postScript:
            self._configOptions['post_command'] = self.postScript
        else:
            self._configOptions['post_command'] = None

    def returnConfig(self):
        """
        Returns running config.
        :return dict: Dict of running config
        """
        self.__writeConfig()
        return self._configOptions


class repoManager:
    def __init__(self):
        """
        Contains all Repository objects.
        Controls when and what gets run
        """
        self.repoQueue = Queue.PriorityQueue(0)
        self.repoList = []

