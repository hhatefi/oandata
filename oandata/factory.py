import configparser
import v20

## Factory for v20 context
#
# It creates v20 context from the configuration parameters read from a
# file
class Factory:
    def __init__(self, config_file):
        self._config=configparser.ConfigParser()
        self._config.read_file(config_file)

    def createContext(self):
        config_default_sec=self._config['DEFAULT'] # the default section of the config
        if 'hostname' not in config_default_sec or 'port' not in config_default_sec or 'token' not in config_default_sec:
            raise ValueError('Required configuration is missing: hostname, port and token are required.')

        use_ssl=config_default_sec.getboolean('ssl') if 'ssl' in config_default_sec else True
        ctx = v20.Context(
            config_default_sec['hostname'],
            config_default_sec.getint('port'),
            use_ssl,
            application='history_fetcher',
            token=config_default_sec['token'],
            datetime_format=config_default_sec['datetime_format']
        )

        return ctx
