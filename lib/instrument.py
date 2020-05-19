from lib.factory import Factory
import pandas as pd

class Instrument:
    def __init__(self, context):
        self._context=context

    @classmethod
    def fromConfigFile(cls, config_file):
        factory=Factory(config_file)
        return cls(factory.createContext())

    ## get candles for \param instrument
    # \param instrument is the name of instrument
    # \param kwargs are the argument controlling the retrieved data
    # \return a list of candle sticks
    def getCandles(self, instrument, **kwargs):
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
            print("No result was found or it is invalid")
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
            print(candleSticks[0].bid)

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
