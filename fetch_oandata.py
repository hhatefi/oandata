#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse
import pandas as pd
from datetime import date

from oandata.instrument import Instrument, Constants, PRICE, GRANULARITY

## creates a parser
#
def createParser():
    parser = argparse.ArgumentParser(description='Fetch historical price data from oanda.')
    parser.add_argument('instrument', type=str, help='the name of instrument')
    parser.add_argument('from_date', type=lambda d: date.fromisoformat(d), help='from date in format YYYY-MM-DD')
    parser.add_argument('to_date', type=lambda d: date.fromisoformat(d), help='to date in format YYYY-MM-DD')
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

    def isValid(self):
        """checks if the object contains valid arguments

        :raise: ValueError if the object is invalid
        """
        if self.config_file is None:
            raise ValueError('No config file is given.')
        if self.from_date >= self.to_date or self.to_date > date.today():
            raise ValueError('Invalid date period: \'{0}\' -- \'{1}\''.format(args.from_date, args.to_date))
        if self.split is not None and self.split < 1:
            raise ValueError('Expected a positive split, but {} is given.'.format(self.split))
        if self.retry < 1:
            raise ValueError('Expected a positive parameter for the number of retries, but {} is given.'.format(self.retry))
        return True

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


## verifies the given arguments
#
# \param args is the arguments to be verified
def verifyArgs(args):
    if args.config_file is None:
        raise ValueError('No config file is given.')
    from_date=date.fromisoformat(args.from_date)
    to_date=date.fromisoformat(args.to_date)
    if from_date >= to_date or to_date > date.today():
        raise ValueError('Invalid date period: \'{0}\' -- \'{1}\''.format(args.from_date, args.to_date))
    if args.split is not None and args.split < 1:
        raise ValueError('Expected a positive split, but {} is given.'.format(args.split))
    if args.retry < 1:
        raise ValueError('Expected a positive parameter for the number of retries, but {} is given.'.format(args.retry))

## fetch historical price data and optically stores them into a file
#
# \param args is the input arguments
def getCandles(args):
    #verifyArgs(args)
    print('[INFO] Reading configurations from "{}"'.format(args.config_file.name))
    ins=Instrument.fromConfigFile(args.config_file)
    # compute the number of subintervals
    subinterval_num=computesIntervalNum(args.from_date, args.to_date, args.granularity) if args.split is None else args.split
    print('[INFO] Splitting the period into {} chunk(s)'.format(subinterval_num))
    subintervals=pd.date_range(start=args.from_date, end=args.to_date, periods=subinterval_num+1)

    # fetching data for each subinterval
    df_list=[]
    for s,e in zip(subintervals[:-1], subintervals[1:]):
        print('[INFO] Fetching data from \'{0}\' to \'{1}\' ...'.format(s.date(),e.date()))
        exception = None # stores exception that may happen during price data fetch
        for _ in range(args.retry):
            try:
                df=ins.getCandles(args.instrument, fromTime=s.date(), toTime=e.date(), granularity=args.granularity, price=args.price)
            except Exception as exp:
                print('[WARN] Failed, retry ...')
                exception=exp
                continue
            exception=None
            break
        if exception is not None:
            print('[ERR] Fetching data from \'{0}\' to \'{1}\' failed, aborting...'.format(s.date(),e.date()))
            raise ValueError('Fetching price data failed. Error:\n{}'.format(exception))
        df_list.append(df)

    # concatenates the dataframes, only if at least one of them is not None
    price_data=pd.DataFrame() if sum([(df is not None)*1 for df in df_list]) == 0 else pd.concat(df_list)

    # storing in file
    if args.output is not None:
        price_data.to_csv(args.output, sep=',', header=True)

    return price_data

def fetch(args):
    """fetch historical price data and optionally stores them into a file

    :param args: the input arguments
    :type args: ArgumentWrapper
    """
    #verifyArgs(args)
    print('[INFO] Reading configurations from "{}"'.format(args.config_file.name))
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
    # check if the arguments are valid
    args.isValid()
    price_data=fetch(args)
    print(price_data)

if __name__ == '__main__':
    main()
