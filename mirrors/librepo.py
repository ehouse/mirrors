import Queue

class repo:
    def __init__(self, name, config):
        """
        Repository Object.
        Gets stored in RepoManager
        :param name: string name of repo
        :param config: dict of configuration values
        """
        # Contains config options
        self._configOptions = config

        ### Config Settings
        # Repo Name
        self.name = name
        # rsync source url
        self.source = self._configOptions['url']
        # rsync args
        self.args = self._configOptions['rsync_args']
        # rsync file destination
        self.destination = self._configOptions['destination']
        # Priority Queue Weight, value between -10 and 10
        self.weight = self._configOptions['weight']
        # Delay before next run is aloud to start
        self.delayTime = self._configOptions['finish_offset']
        # list of hours sync must happen on
        #self.scrictTime = self._configOptions['hourly_run']
        # Pre-bash Script
        self.preScript = self._configOptions['pre_command']
        # Post-Bash Script
        self.postScript = self._configOptions['post_command']

        ### Job Stats
        # Start time of last sucessful run
        self.lastRun = None
        # Length of last run
        self.lastRunLength = None
        # Repo Avg run length
        self.runAvg = None

    def returnConfig():
        """
        Returns running config.
        :return dict: Dict of running config
        """
        return self._configOptions


class repoManager:
    def __init__(self):
        """
        Contains all Repository objects.
        Controls when and what gets run
        """
        self.repoQueue = Queue.PriorityQueue(0)
        self.repoList = []

