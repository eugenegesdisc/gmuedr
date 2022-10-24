import importlib

command_list = {
    "convert": {"modulename":"command.command_convert","classname":"CommandConvert"},
    "combine": {"modulename":"command.command_combine","classname":"CommandCombine"},
    "combine2": {"modulename":"command.command_combine2","classname":"CommandCombine2"}
}

class CommandFactory():

    @staticmethod
    def create(command, args):
        the_command = command_list.get(command)
        return CommandFactory.str_to_class(
            the_command.get("modulename"),
            the_command.get("classname"))(args)

    @staticmethod
    def str_to_class(module_name, class_name):
        """Return a class instance from a string reference"""
        try:
            module_ = importlib.import_module(module_name)
            try:
                class_ = getattr(module_, class_name)
            except AttributeError:
                logging.error('Class does not exist')
        except ImportError:
            logging.error('Module does not exist')
        return class_ or None
