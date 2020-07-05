import configparser
import v20

## Factory for v20 context
#
# It creates v20 context from the configuration parameters read from a
# file
class Factory:
    def __init__(self, config):
        """create an instance of a Factory

        :param config: the configuration dictionary that must contain
        'hostname' and 'token' keys with relevant values. The value
        associated with 'hostname' refers to the hostname of v20 REST
        server and that associated with 'token' is the token used fo
        making request to the v20 server. Both values must be of
        string type. Other optinal keys and values are

        * 'port' -> int
        * 'ssl' -> bool
        * 'application' -> str
        * 'decimal_number_as_float' -> bool
        * 'stream_chunk_size' -> int
        * 'stream_timeout' -> int
        * 'datetime_format' -> str
        * 'poll_timeout' -> int

        :type config: dict

        """
        self._config=config

    @classmethod
    def fromConfigFile(cls, config_file):
        """creates a factory accordng to the configuration given in `config_file`

        :param config_file: the configuration file, which is an
        iterable yielding unicode string, e.g. a file opened in text
        mode (`open('config.conf')`). The file has a [DEFAULT] section
        with at least 'hostname' and 'token' given. Here is a complete
        example for the file::

        	[DEFAULT]
    		# hostname is mandatory
		hostname=api-fxpractice.oanda.com
        	port=443
	        ssl=True
        	application=""
		# token is mandatory
	        token=xxxxxxxxxxx-xxxxxxxxxxxx
        	decimal_number_as_float=True
	        stream_chunk_size=512
        	stream_timeout=10
	        datetime_format="RFC3339"
        	poll_timeout=2

        :type config_file: an iterable yielding unicode string
        """
        config_parser=configparser.ConfigParser()
        config_parser.read_file(config_file)
        section_default= config_parser['DEFAULT']
        if 'hostname' not in section_default or 'token' not in section_default:
            raise ValueError('Required configuration is missing: hostname and token are required.')

        config={}
        # set hostname
        config['hostname']=section_default['hostname']

        # set port number
        if 'port' in section_default:
            config['port']=section_default.getint('port')

        # set ssl
        if 'ssl' in section_default:
            config['ssl']=section_default.getboolean('ssl')

        # set token
        config['token']=section_default['token']

        # decimal_number_as_float
        if 'decimal_number_as_float' in section_default:
            config['decimal_number_as_float']=section_default.getboolean('decimal_number_as_float')

        # set stream_chunk_size
        if 'stream_chunk_size' in section_default:
            config['stream_chunk_size']=section_default.getint('stream_chunk_size')

        # set stream_timeout
        if 'stream_timeout' in section_default:
            config['stream_timeout']=section_default.getint('stream_timeout')

        # set datetime_format
        if 'datetime_format' in section_default:
            config['datetime_format']=section_default['datetime_format']

        # set poll_timeout
        if 'poll_timeout' in section_default:
            config['poll_timeout']=section_default.getint('poll_timeout')

        return cls(config)

    def createContext(self):
        return v20.Context(**self._config)
