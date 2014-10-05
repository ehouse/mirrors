from cmd import Cmd
import logging
from mirrors.repo import RepoError


class Console(Cmd):
    def __init__(self, repo_manager):
        Cmd.__init__(self)
        self.prompt = "> "
        self.intro = "Welcome to the mirrors interactive shell. Type help to display commands."
        self.repo_manager = repo_manager

    def do_status(self, *args):
        """Prints status table or the status of an individual sync."""
        name = args[0]
        if name:
            try:
                print self.repo_manager.status(name)
            except RepoError as e:
                print e.message
        else:
            for key in self.repo_manager.gen_repo():
                self.do_status(key.name)

    def do_list(self, *args):
        """List all of the loaded repos."""
        for key in self.repo_manager.gen_repo():
            print key

    def do_enqueue(self, *args):
        """Add repo onto the end of the async queue."""
        name = args[0]
        if name == "all":
            for repo in self.repo_manager.gen_repo():
                self.do_enqueue(repo.name)
        elif name:
            try:
                self.repo_manager.enqueue(name)
                print("{0} added to sync queue".format(name))
            except RepoError as e:
                print(e.message)
        else:
            print("Requires a repo name as an argument.")
    do_start = do_enqueue

    def do_activate(self, *args):
        """Activate repo for syncing."""
        name = args[0]
        if name:
            try:
                self.repo_manager.activate(name)
            except RepoError as e:
                print e.message
        else:
            print("Requires a repo name as an argument.")

    def do_deactivate(self, *args):
        """Deactivate repo from syncing."""
        name = args[0]
        if name:
            try:
                self.repo_manager.deactivate(name)
            except RepoError as e:
                print e.message
        else:
            print("Requires a repo name as an argument.")

    def do_print(self, *args):
        """Print config and status events.

        TODO
        """
        pass

    def do_config(self, *args):
        """Edit configuration running settings.

        TODO
        """
        pass

    def do_write(self, *args):
        """Write configuration settings to file.

        TODO
        """
        pass

    def do_add(self, *args):
        """Add repo from running config.

        TODO
        """
        pass

    def do_del(self, *args):
        """Delete repo from running config.

        TODO
        """
        pass

    def do_reload(self, *args):
        """Reload either individual or entire config.

        TODO
        """
        pass

    def do_terminate(self, *args):
        """Send SIGTERM to rsync process."""
        if args[0]:
            self.repo_manager.get_repo(args[0]).terminate()
        else:
            print("Missing required argument: Repo")
    do_kill = do_terminate

    def do_forcekill(self, *args):
        """Send SIGKILL to rsync process."""
        if args[0]:
            self.repo_manager.get_repo(args[0]).kill()
        else:
            print("Missing required argument: Repo")

    def do_exit(self, *args):
        """Stops all syncs and terminates mirrors."""
        return True
    do_quit = do_exit

    def postloop(self):
        """postloop cleanup."""
        # Cleanup Process
        for key in self.repo_manager.gen_repo():
            key.terminate()
        print("Terminating mirrors process")
        logging.debug("Process Terminated via REPL")
