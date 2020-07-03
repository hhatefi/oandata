#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, argparse
from datetime import date
import pandas as pd

from oandata.instrument import Instrument

_GRANULARITY = [
    'S5', 'S10', 'S15', 'S30',                   # seconds e.g. S5 denotes 5 second granularity
    'M1', 'M2', 'M4', 'M5', 'M10', 'M15', 'M30', # minutes e.g. M1 denotes one minute granularity
    'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'H12',   # hours e.g. H1 denotes one hour granularity
    'D',                                         # daily
    'W',                                         # weekly
    'M']                                         # montly
_PRICE = ['B',  # bid
          'A',  # ask
          'M']  # mid
_RETRY_NUM = 3 # the default number of retries when a request fails

## gets the granularity in seconds
#
# \param granularity is one of the granularities defined in _GRANULARITY
def getGranularityInSec(granularity):
    if granularity[0] == 'S':
        return int(granularity[1:])
    elif granularity[0] == 'M':
        return int(granularity[1:]) * 60
    elif granularity[0] == 'H':
        return int(granularity[1:]) * 60 * 60
    elif granularity[0] == 'D':
        return 60 * 60 * 24
    elif granularity[0] == 'W':
        return 60 * 60 * 24 * 7
    elif granularity[0] == 'M':
        return 60 * 60 * 24 * 30
    else:
        raise ValueError('Unexpected granularity "{0}"'.format(granularity))

## computes the default number of intervals
#
# If the period between @param start and @param end is long and @param
# granularity is fine, i.e. historical price data contains lots of
# candle sticks, oanda will return "Bad Request". To mitigate the
# problem, the period can be split into several sub-intervals, each
# holding a fewer candle sticks. The number of candle sticks within
# each sub-interval is kept at most _MAX_CANDLE_STICKS (unless the
# sub-interval is smaller than a day.) This function computes the
# number of those sub-intervals.
def computesIntervalNum(start, end, granularity):
    _MAX_CANDLE_STICKS = 2500 # the maximum number of candle sticks allowed in each request
    delta=date.fromisoformat(end) - date.fromisoformat(start)
    delta_sec=delta.total_seconds()
    granularity_sec=getGranularityInSec(granularity)
    return int(delta_sec / granularity_sec / _MAX_CANDLE_STICKS) + 1

## creates a parser
#
def getParser():
    parser = argparse.ArgumentParser(description='Fetch historical price data from oanda.')
    parser.add_argument('instrument', type=str, help='the name of instrument')
    parser.add_argument('from_date', help='from date in format YYYY-MM-DD')
    parser.add_argument('to_date', help='to date in format YYYY-MM-DD')
    parser.add_argument('--config_file', '-c', type=argparse.FileType('r'), default=None, help='the path to the config file. Giving a proper config file is mandatory.')
    parser.add_argument('--output', '-o', type=str, help='csv output filename')
    parser.add_argument('--granularity', '-g', choices=_GRANULARITY, default='D', help='granularity of historical price')
    parser.add_argument('--price', '-p', choices=_PRICE, default='M', help='Bid, ask or mid prices. The default is mid.')
    parser.add_argument('--split', '-s', type=int, default=None, help='if given, split the period into the given number of sub-intervals and fetch historical data over each sub-interval individually. If not given, the number of splits is comuputed according to the period length and granularity.')
    parser.add_argument('--retry', '-r', type=int, default=_RETRY_NUM, help='the number of retries, when a fetch request failed (default {}).'.format(_RETRY_NUM))
    return parser

## verifies the given arguments
#
# \param args is the argumnet to be verified
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
    verifyArgs(args)
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

def main():
    parser=getParser()
    args=parser.parse_args()
    price_df=getCandles(args)
    print(price_df)

    try:
        pass
    except Exception as exp:
        print("[ERR] An error occured: \n {}".format(exp))
        print("[INFO] To see the list of command line arguments, run the program with `-h`.")
        sys.exit(1)

if __name__ == '__main__':
    main()
