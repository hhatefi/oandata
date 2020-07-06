import unittest, configparser
from context import factory as fc

class file_mock:
    """mocks a config file
    """
    def __init__(self, s):
        self._s=s

    def __iter__(self):
        self._line_iter=self._s.split('\n')
        return iter(self._line_iter)

    def __next__(self):
        next(self._line_iter)

    def read(self):
        return self._s

class FactoryTest(unittest.TestCase):
    def test_from_config_file(self):
        s="" # no default section
        f=file_mock(s)

        with self.assertRaises(ValueError):
            fc.Factory.fromConfigFile(f)

        s="hostname=www.example.com" # no default section
        f=file_mock(s)

        with self.assertRaises(configparser.MissingSectionHeaderError):
            fc.Factory.fromConfigFile(f)

        s="[DEFAULT]\nhostname=www.example.com" # no token
        f=file_mock(s)

        with self.assertRaises(ValueError):
            fc.Factory.fromConfigFile(f)

        s="[DEFAULT]\nhostname=www.example.com\ntoken=xxxx" # fine
        f=file_mock(s)

        fac=fc.Factory.fromConfigFile(f)
        self.assertEqual(fac._config['hostname'], 'www.example.com')
        self.assertEqual(fac._config['token'], 'xxxx')

        s="[DEFAULT]\nhostname=www.oanda.com\ntoken=aaaaa\nport=234\nssl=False" # fine
        f=file_mock(s)

        fac=fc.Factory.fromConfigFile(f)
        self.assertEqual(fac._config['hostname'], 'www.oanda.com')
        self.assertEqual(fac._config['token'], 'aaaaa')
        self.assertEqual(fac._config['port'], 234)
        self.assertFalse(fac._config['ssl'])

        s="[DEFAULT]\nhostname=nothing\ntoken=----\nport=100\nssl=True\napplication=fetcher\ndecimal_number_as_float=no\nstream_chunk_size=300\nstream_timeout=1\ndatetime_format=TTT9\npoll_timeout=0" # fine
        f=file_mock(s)

        fac=fc.Factory.fromConfigFile(f)
        self.assertEqual(fac._config['hostname'], 'nothing')
        self.assertEqual(fac._config['token'], '----')
        self.assertEqual(fac._config['port'], 100)
        self.assertTrue(fac._config['ssl'])
        self.assertEqual(fac._config['application'], "fetcher")
        self.assertFalse(fac._config['decimal_number_as_float'])
        self.assertEqual(fac._config['stream_chunk_size'], 300)
        self.assertEqual(fac._config['stream_timeout'], 1)
        self.assertEqual(fac._config['datetime_format'], "TTT9")
        self.assertEqual(fac._config['poll_timeout'], 0)


if __name__ == '__main__':
    unittest.main()
