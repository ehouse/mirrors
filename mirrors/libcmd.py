import cmd


class Console(cmd.Cmd):
    def __init__(self, repo_manager):
        cmd.Cmd.__init__(self)
        self.prompt = "> "
        self.intro = "Welcome to the mirrors interactive shell. Type help to display commands"

    def do_status(self, args):
        """Prints status table or status of individual sync"""
        pass

    def do_exit(self, args):
        """Stops all syncs and terminates mirrors"""
        exit(0)

    def do_quit(self, args):
        self.do_exit(None)
