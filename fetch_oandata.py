#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse, logging
import pandas as pd
from datetime import date

from oandata.instrument import Instrument, Constants, PRICE, GRANULARITY, isoStrToDate

### configure logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

## creates a parser
#
def createParser():
    parser = argparse.ArgumentParser(description='Fetch historical price data from oanda.')
    parser.add_argument('instrument', type=str, help='the name of instrument')
    parser.add_argument('from_date', type=lambda d: isoStrToDate(d), help='from date in format YYYY-MM-DD')
    parser.add_argument('to_date', type=lambda d: isoStrToDate(d), help='to date in format YYYY-MM-DD')
    parser.add_argument('--config_file', '-c', type=argparse.FileType('r'), default=None, help='the path to the config file. Giving a proper config file is mandatory.')
    parser.add_argument('--output', '-o', type=str, help='csv output filename')
    parser.add_argument('--granularity', '-g', choices=GRANULARITY, default=Constants.DEFAULT_GRANULARITY, help='granularity of historical price')
    parser.add_argument('--price', '-p', choices=PRICE, default=Constants.DEFAULT_PRICE, help='Bid, ask or mid prices. The default is mid.')
    parser.add_argument('--split', '-s', type=int, default=None, help='if given, split the period into the given number of sub-intervals and fetch historical data over each sub-interval individually. If not given, the number of splits is comuputed according to the period length and granularity.')
    parser.add_argument('--retry', '-r', type=int, default=Constants.DEFAULT_RETRY, help='the number of retries, when a fetch request failed (default {}).'.format(Constants.DEFAULT_RETRY))
    return parser

class ArgumentWrapper:
    """a wrapper around arguments parsed from input

    This class serves as a wrapper around input arguments. It provides
    an abstraction layer over the way `argparse` handles arguments.
    """
    def __init__(self, args):
        """initialize an instance of ArgumentWrapper

        :param args: the arguments parsed by `argparse` parser
        :type args: argparse.Namespace or something with the same structure
        """
        self.instrument=args.instrument
        self.from_date=args.from_date
        self.to_date=args.to_date
        self.config_file=args.config_file
        self.output=args.output
        self.granularity=args.granularity
        self.price=args.price
        self.split=args.split
        self.retry=args.retry

    def getArgs(self):
        """make a dictionary of arguments and their values

        It makes a dictionary of arg_name: arg_val to be passed to
        `Instrumnet.getCandle`. It only contains keyword arguments.
        """
        return {
            'granularity': self.granularity,
            'price': self.price,
            'split':self.split,
            'retry':self.retry,
            }

def fetch(args):
    """fetch historical price data and optionally stores them into a file

    :param args: the input arguments
    :type args: ArgumentWrapper
    """
    #verifyArgs(args)
    logging.info('Reading configurations from "{}"'.format(args.config_file.name))
    ins=Instrument.fromConfigFile(args.config_file)

    # get the keyworded arguments to be passed to getCandle
    kwargs=args.getArgs()
    # compute the number of subintervals
    price_data=ins.getCandles(args.instrument, args.from_date, args.to_date, **kwargs)

    # storing in file
    if args.output is not None:
        price_data.to_csv(args.output, sep=',', header=True, index_label='Time')

    return price_data

def main():
    parser=createParser()
    args=ArgumentWrapper(parser.parse_args())
    price_data=fetch(args)

    logging.info('Printing price data...')
    print(price_data)

if __name__ == '__main__':
    main()
