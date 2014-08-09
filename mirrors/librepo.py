import Queue

class Repo:
    def __init__(self, config):
        """
        Repository Object.
        Gets stored in RepoManager
        """
        # Contains config options
        self.config_options = config

        ### Config Settings
        # Repo Name
        self.name = None
        # Priority Queue Weight, value between -10 and 10
        self.weight = None
        # Delay before next run is aloud to start
        self.delayTime = None
        # list of hours sync must happen on
        self.scrictTime = []
        # Pre-bash Script
        self.preScript = None
        # Post-Bash Script
        self.postScript = None

        ### Job Stats
        # Start time of last sucessful run
        self.lastRun = None
        # Length of last run
        self.lastRunLength = None
        # Repo Avg run length
        self.runAvg = None


class RepoManager:
    def __init__(self):
        """
        Contains all Repository objects.
        Controls when and what gets run
        """
        self.repoQueue = Queue.PriorityQueue(0)
        self.repoList = []

