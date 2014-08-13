from cmd import Cmd
import logging


class Console(Cmd):
    def __init__(self, repo_manager):
        Cmd.__init__(self)
        self.prompt = "> "
        self.intro = "Welcome to the mirrors interactive shell. Type help to display commands"

        self.repo_manager = repo_manager

    def do_status(self, name):
        """Prints status table or the status of an individual sync"""
        # Current system is a placeholder. Needs to be reworked
        # Will return a lot more information
        if name:
            repo = self.repo_manager.repo(name)
            if repo.is_alive():
                print("{0} is currently syncing".format(name))
            else:
                print("{0} is currently Sleeping".format(name))
        else:
            for key in self.repo_manager.repo_dict:
                self.do_status(key)

    def do_list(self, args):
        """List all of the loaded repos"""
        for key in self.repo_manager.repo_dict:
            print key

    def do_enqueue(self, name):
        """Add repo onto the end of the async queue"""
        if name:
            if self.repo_manager.enqueue(name):
                print("{0} added to sync queue".format(name))
            else:
                print("Failed to enqueue {0}, already in queue".format(name))
        else:
            print("enqueue requires a repo")

    def do_print(self, args):
        """Print config and status events"""
        args = args.split()
        if args:
            if args[0] == "logs":
                if args[1]:
                    name = args[1]
                    print(self.repo_manager.repo(name).get_logs()[0])
            elif args[0] is "errors":
                if args[1]:
                    name = args[1]
                    print(self.repo_manager.repo(name).get_logs()[1])


    def do_terminate(self, args):
        """Send SIGTERM to rsync process"""
        name = args
        repo = self.repo_manager.repo(name) 
        repo.terminate()

    def do_kill(self, args):
        """Send SIGKILL to rsync process"""
        name = args
        repo = self.repo_manager.repo(name)
        repo.terminate()

    def do_exit(self, args):
        """Stops all syncs and terminates mirrors"""
        exit(0)

    def do_quit(self, args):
        """Stops all syncs and terminates mirrors"""
        self.do_exit(None)

    def postloop(self):
        print("Terminating mirrors process")
        logging.debug("Process Terminated via REPL")

