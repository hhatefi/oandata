fetch_oandata
=============

It fetches price data from Oanda using its python bindings for [REST
API v20](https://developer.oanda.com/rest-live-v20/introduction/).

Requirements
------------

To use the fetcher, you need python 3 with packages `v20` and `pandas` installed. They can be installed individually or by

```SHELL
pip install -r requirements.txt
```

Configuration
-------------

Configuration parameters for communicating with Oanda servers are
stored in a config file. A sample config file may look like:

```SHELL
[DEFAULT]
hostname = api-fxpractice.oanda.com
port = 443
ssl = true
token = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
datetime_format = RFC3339
```

where `token` is required to grant access to the REST API. See [developer page](https://developer.oanda.com/rest-live-v20/introduction/) of
Oanda website to see how to sign up and get a free access token.

Examples
--------

After preparing a config file, you can run fetcher to get price data. For instance,

```SHELL
python3 fetch_oandata.py EUR_USD 2020-04-05 2020-05-16 -g M30 -c /path/to/config -o /path/to/csv
```

fetches the price of EURO in USD within the given period with
granularity of 30 minutes. The result is stored in the given CSV file.
By default the mid price of the instrument is fetched. To obtain bid
or ask prices, `-p B` or `-p A` can be added to the list of arguments,
respectively. To see the supported granularity and a complete list of
arguments, run

```SHELL
python3 fetch_oandata -h
```

If the given period is long and granularity is fine, i.e. historical
price data contain lots of candle sticks, fetching them will sometimes
get failed. To mitigate the problem, the period is split into several
sub-intervals, each holding a fewer number of candle sticks. The
number of those sub-intervals can be set by `--split` or `-s`. Adding
`-s 10` to the list of arguments above, for example, splits the period
into 10 sub-intervals of roughly the same size and fetch the prices
for each sub-interval individually before merging them together. If it
is not set, it will be computed according to the given period and
granularity.

Fetch of price data for each sub-interval can nevertheless fail for
other reasons. In this case, the fetcher retries again. The number of
attempts before reporting failure can be set via `-r`.
