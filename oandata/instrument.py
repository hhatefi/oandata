from datetime import date, timedelta
import pandas as pd
import logging

from oandata.factory import Factory

### configure logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

# the set of valid granularities
GRANULARITY = (
    'S5', 'S10', 'S15', 'S30',                   # seconds e.g. S5 denotes 5 second granularity
    'M1', 'M2', 'M4', 'M5', 'M10', 'M15', 'M30', # minutes e.g. M1 denotes one minute granularity
    'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'H12',   # hours e.g. H1 denotes one hour granularity
    'D',                                         # daily
    'W',                                         # weekly
    'M',                                         # montly
)

# the set of valid price types
PRICE = (
    'B',  # bid
    'A',  # ask
    'M',  # mid
)

class Constants:
    DEFAULT_RETRY=3          # the default number of retries when a request fails
    DEFAULT_GRANULARITY='D'  # the default price granularity
    DEFAULT_PRICE='M'        # the
    MAX_CANDLE_STICKS = 2500 # the maximum number of candle sticks allowed in each request

def isoStrToDate(d):
    """converts date from iso format to datetime.date

    This method was added since python 3.5 does not provide
    datetime.date.fromisoformat.

    :param d: date specified in iso format YYYY-MM-DD
    :type d: str
    :return: the coverted date object
    :rtype: datetime.date

    """
    return pd.Timestamp(d).to_pydatetime().date()

def getGranularityInSec(granularity):
    """gets the granularity in seconds

    :param granularity: price granularity, which can be one of the
    granularities defined in `GRANULARITY`

    :type granularity: str
    :return: the granularity in seconds
    :rtype: int
    :raise: ValueError
    """
    if granularity not in GRANULARITY:
        raise ValueError('Unexpected granularity "{0}"'.format(granularity))

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
    else: # it must be 'M'
        return 60 * 60 * 24 * 30

def computeIntervalNum(start, end, granularity):
    """computes the number of splits between `start` and `end`

    If the period between @param start and @param end is long and
    @param granularity is fine, i.e. historical price data contains
    lots of candle sticks, oanda will return "Bad Request". To
    mitigate the problem, the period can be split into several
    sub-intervals, each holding a fewer candle sticks. The number of
    candle sticks within each sub-interval is kept at most
    `Constants.MAX_CANDLE_STICKS` (unless the sub-interval is smaller
    than a day.) This function computes the number of those
    sub-intervals.

    :param start: the first day on which price data is downloaded
    :param end: the last day on which price data is downloaded
    :param granularity: the granularity of price data
    :type start: datetime.date
    :type end: dattime.date
    :type granularity: str, it must holds that `granularity in GRANULARITY`
    :return: the number of periods
    :rtype: int
    """
    delta=end - start + timedelta(days=1)
    delta_sec=delta.total_seconds()
    granularity_sec=getGranularityInSec(granularity)
    return min(int(delta_sec / granularity_sec / Constants.MAX_CANDLE_STICKS) + 1, delta.days)

def getSplits(start, end, splits):
    """split time interval [start, end] into splits and returns them as a list
    :param start: the first day in the interval
    :param end: the last day in the interval
    :param splits: the number of splits
    :type start: datetime.date
    :type end: datetime.date
    :type splits: positive int
    :return: the list of pairs of (start,end) for each split
    :rtype: list
    """
    delta=end - start + timedelta(days=1)
    period=timedelta(seconds=delta.total_seconds() / splits).days
    d=start
    sub_int=[]
    while d <= end:
        e = min(d + timedelta(days=period), end)
        sub_int.append((d, e))
        d = e + timedelta(days=1)

    return sub_int

class Instrument:
    def __init__(self, context):
        self._context=context

    @classmethod
    def fromConfigFile(cls, config_file):
        factory=Factory.fromConfigFile(config_file)
        return cls(factory.createContext())

    @classmethod
    def fromConfigDict(cls, config_dict):
        factory=Factory(config_dict)
        return cls(factory.createContext())

    def _getCandles(self, instrument, **kwargs):
        """retrieves and returns candle data for an instrument
        :param instrument: is the name of instrument
        :param kwargs: the argument controlling the retrieved data that is directly passed to v20.Context.instrument.candles
        :return: a dataframe of candle sticks
        :rtype: pandas.DataFrame
        """
        # The following function send a GET request and then process,
        # fill out and return the response.
        resp=self._context.instrument.candles(instrument, **kwargs)

        # On success response.status will be 200 and
        # response.body["candles"] should contain a list of candle
        # sticks. Method response.get(f,s) checks if the status equals
        # s and returns response.body[f].
        candleSticks=resp.get("candles", 200)

        # check the validity of candleSticks, it should be a list of
        # as least one candle stick
        if candleSticks is None or not isinstance(candleSticks, list) or len(candleSticks)==0:
            logging.warn("No result was found or it is invalid")
            return None

        # convert candleSticks to a dataframe
        indexes=[pd.Timestamp(cs.time) for cs in candleSticks]
        candleSticksDataFrame={}
        priceAction=None
        if candleSticks[0].bid is not None:
            candleSticksDataFrame['Open']=[cs.bid.o for cs in candleSticks]
            candleSticksDataFrame['Close']=[cs.bid.c for cs in candleSticks]
            candleSticksDataFrame['Low']=[cs.bid.l for cs in candleSticks]
            candleSticksDataFrame['High']=[cs.bid.h for cs in candleSticks]

        if candleSticks[0].ask is not None:
            candleSticksDataFrame['Open']=[cs.ask.o for cs in candleSticks]
            candleSticksDataFrame['Close']=[cs.ask.c for cs in candleSticks]
            candleSticksDataFrame['Low']=[cs.ask.l for cs in candleSticks]
            candleSticksDataFrame['High']=[cs.ask.h for cs in candleSticks]

        if candleSticks[0].mid is not None:
            candleSticksDataFrame['Open']=[cs.mid.o for cs in candleSticks]
            candleSticksDataFrame['Close']=[cs.mid.c for cs in candleSticks]
            candleSticksDataFrame['Low']=[cs.mid.l for cs in candleSticks]
            candleSticksDataFrame['High']=[cs.mid.h for cs in candleSticks]
        candleSticksDataFrame['Volume']=[cs.volume for cs in candleSticks]
        candleSticksDataFrame['Complete']=[cs.complete for cs in candleSticks]
        return pd.DataFrame(candleSticksDataFrame, index=indexes)

    def getCandles(self, instrument, from_date, to_date,
                   granularity=Constants.DEFAULT_GRANULARITY,
                   price=Constants.DEFAULT_PRICE,
                   split=None, # let the number of splits is automatically estimated
                   retry=Constants.DEFAULT_RETRY, **kwargs):
        """fetch candle data from OANDA with

        This method fetches price of `instrument` within time period
        `from_date` to `to_date` and returns the result as `pandas.DataFrame`.

        :param instrument: the name of instrument e.g. 'EUR_USD' or 'DE30_EUR'
        :param from_date: the first date on which price data is recorded
        :param to_date: the last date on ehich price data is recorded
        :param granularity: the frequency of price data
        :param price: indictes which of bid, ask r mid price is recorded
        :param split: the number of splits
        :param retry: the maximum number of retries if downloading fails before giving up

        :type instrument: str
        :type from_date: str of format 'YYYY-MM-DD' or datetime.date
        :type to_date: str of format 'YYYY-MM-DD' or datetime.date
        :type granularity: str, must be one of the available options in `GRANULARITY`
        :type price: str, must be one of the available options in `PRICE`
        :type split: int, must be positive
        :type retry: int, must be positive

        :raise: ValueError if an argument is not valid or fetching
        price data failed after retries, BadRequest if the request to
        v20 REST server is not valid, for instance the instrument name
        is not valid.
        """
        # step 1: verify and convert arguments

        # check and convert from_date
        if isinstance(from_date, str):
            from_date=isoStrToDate(from_date)
        elif not isinstance(from_date, date):
            ValueError("'from_date' must be either a string in 'YYYY-MM-DD' format, or an object of type datetime.date")

        # check and convert to_date
        if isinstance(to_date, str):
            to_date=isoStrToDate(to_date)
        elif not isinstance(to_date, date):
            raise ValueError("'to_date' must be either a string in 'YYYY-MM-DD' format, or an object of type datetime.date")

        # check the duration
        if from_date >= to_date or to_date > date.today():
            raise ValueError('Invalid date period: \'{0}\' -- \'{1}\''.format(from_date, to_date))

        # check granularity
        if not isinstance(granularity, str) or granularity not in GRANULARITY:
            raise ValueError('Given granularity \'{}\' is not supported.'.format(granularity))

        # check price
        if not isinstance(price, str) or price not in PRICE:
            raise ValueError('Given price type \'{}\' is not supported.'.format(price))

        # check split
        if split is not None and (not isinstance(split, int) or split < 1):
            raise ValueError('Expected a positive split, but {} is given.'.format(self.split))

        # check retry
        if not isinstance(retry, int) or retry < 1:
            raise ValueError('Expected a positive parameter for the number of retries, but {} is given.'.format(self.retry))

        # step 2: split the duration into splits
        # compute the number of splits (splits of [from_date, to_date])
        split_num=computeIntervalNum(from_date, to_date, granularity) if split is None else split
        logging.info('Splitting the period into {} chunk(s)'.format(split_num))
        split_intervals=getSplits(start=from_date, end=to_date, splits=split_num+1)

        # step 3: fetching data for each split
        df_list=[] # the list of dataframes, each holds price data for the corresponding split
        for s,e in split_intervals:
            logging.info('Fetching data from \'{0}\' to \'{1}\' ...'.format(s,e))
            exception = None # stores exception that may happen during price data fetch
            for _ in range(retry):
                try:
                    df=self._getCandles(instrument, fromTime=s, toTime=e, granularity=granularity, price=price)
                except Exception as exp:
                    logging.warn('Failed, retry ...')
                    exception=exp
                    continue
                exception=None
                break
            if exception is not None:
                logging.error('Fetching data from \'{0}\' to \'{1}\' failed, aborting...'.format(s,e))
                raise ValueError('Fetching price data failed. Error:\n{}'.format(exception))
            df_list.append(df)

        # step 4: concatenating the fetched dataframes, only if at least one of them is not None
        return pd.DataFrame() if sum([(df is not None)*1 for df in df_list]) == 0 else pd.concat(df_list)
