import configparser as CFG


class Config(CFG.ConfigParser):

    @staticmethod
    def load(cli_args):
        """ Convert command-line arguments and config file into a global application configuration object."""
        config = Config()
    
        for key, value in vars(cli_args).items():
            config.set("DEFAULT", key, str(value))
    
        if cli_args.config:
            config.read(cli_args.config.name)
        return config

    @property
    def verbose(self):
        return self['DEFAULT'].getboolean('verbose')
