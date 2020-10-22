# gbpchf_strategy.py

# GBP/CHF trading simulation

import pandas as pd

from statistics import mean, stdev
from utils import returns_calculation


def gbpchf_trading(cointegration_data, prices):
    """Simulate trading by following the algorithm:
        1. check current spread, if it's above one standard deviation, short the spread on the current day, else long
        2. close open position when mean of spread is reached, or before opening a new one

        :param cointegration_data is a dict containing cointegration data for relevant time period
        :param prices is a dict with bids and asks, in order to short or long the spread accordingly
        :return returns_series -> a list
    """

    mean_of_spread = mean(cointegration_data['historical_spreads'])
    st_dev_of_spread = stdev(cointegration_data['historical_spreads'])
    trading_period_spreads = cointegration_data['trading_spreads']
    n = len(trading_period_spreads)
    position_prices = []

    open_position = False
    long = False

    entries = convergences = 0

    business_days = 252
    # total_returns = [0] * business_days
    returns = {}
    for day in range(business_days):
        returns[day] = 0

    for i in range(1, n):  # i = tomorrow, i - 1 = today, i - 2 = yesterday
        current_spread = trading_period_spreads[i - 1]
        next_spread = trading_period_spreads[i]
        # check if any position is open, if so close it if it has crossed the mean, else keep open
        if open_position is True:
            bigger_spread = max(next_spread, current_spread)
            smaller_spread = min(next_spread, current_spread)
            diff = bigger_spread - smaller_spread
            bigger_spread_current_from_mean = max(current_spread, mean_of_spread)
            smaller_spread_current_from_mean = min(current_spread, mean_of_spread)
            diff_current_spread_from_mean = bigger_spread_current_from_mean - smaller_spread_current_from_mean

            if diff > diff_current_spread_from_mean:  # we had a crossing so close position and calculate returns
                open_position = False
                convergences += 1
                returns_data = [
                    {
                        # not invested in EUR/CHF since I'm trading only GBP/CHF in this session
                        'I': 0,
                        'current_close': prices['eurchf_bids'][i - 1] if long else prices['eurchf_asks'][i - 1],
                        'previous_close': position_prices[0],
                        'cointegration_weight': cointegration_data['renormalised_beta_EURCHF'],
                    },
                    {
                        # not invested in EUR/GBP since I'm trading only GBP/CHF in this session
                        'I': 0,
                        'current_close': prices['eurgbp_bids'][i - 1] if long else prices['eurgbp_asks'][i - 1],
                        'previous_close': position_prices[2],
                        'cointegration_weight': cointegration_data['renormalised_beta_EURGBP'],
                    },
                    {
                        # for simplicity, we trade only the GBP/CHF pair so the value of I is either 1 = long
                        # or -1 = short, and not 0. It's trivial to apply the logic to the other two pairs
                        'I': 1 if long else -1,
                        'current_close': prices['gbpchf_bids'][i - 1] if long else prices['gbpchf_bids'][i - 1],
                        'previous_close': position_prices[1],
                        'cointegration_weight': cointegration_data['renormalised_beta_GBPCHF'],
                    },
                ]

                daily_return = returns_calculation(returns_data)
                returns[i - 1] = daily_return

            else:  # no crossing so keep position open
                continue

        distance_from_st_dev = abs(current_spread) - abs(st_dev_of_spread)
        if distance_from_st_dev > 0:
            open_position = True
            entries += 1
            sign = current_spread - st_dev_of_spread
            if sign > 0:  # short the spread
                long = False
                position_prices = prices['eurchf_bids'][i - 1], prices['gbpchf_bids'][i - 1], prices['eurgbp_bids'][i - 1]
            else:         # long the spread
                long = True
                position_prices = prices['eurchf_asks'][i - 1], prices['gbpchf_asks'][i - 1], prices['eurgbp_asks'][i - 1]

    return_series = []
    for day, return_val in returns.items():
        return_series.append(return_val)
    return return_series

if __name__ == '__main__':
    full_range = pd.read_csv('data.csv')
    full_range['obs'] = pd.to_datetime(full_range['obs'])

    historical_spreads = full_range['uhat2_2009_2010'][7:265].tolist()
    trading_spreads = full_range['uhat2_2009_2010'][265:525].tolist()

    coint_results_2009_2010 = {
        'renormalised_beta_EURCHF': 1.0,
        'renormalised_beta_GBPCHF': -0.85868,
        'renormalised_beta_EURGBP': -1.6546,
        'historical_spreads': historical_spreads,
        'trading_spreads': trading_spreads
    }

    eurchf_bids, eurchf_asks = full_range['EURCHFClose_bid'][265:525], full_range['EURCHFClose_ask'][265:525]
    gbpchf_bids, gbpchf_asks = full_range['GBPCHFClose_bid'][265:525], full_range['GBPCHFClose_ask'][265:525]
    eurgbp_bids, eurgbp_asks = full_range['EURGBPClose_bid'][265:525], full_range['EURGBPClose_ask'][265:525]
    prices = {
        'eurchf_bids': eurchf_bids.tolist(), 'eurchf_asks': eurchf_asks.tolist(),
        'gbpchf_bids': gbpchf_bids.tolist(), 'gbpchf_asks': gbpchf_asks.tolist(),
        'eurgbp_bids': eurgbp_bids.tolist(), 'eurgbp_asks': eurgbp_asks.tolist()
    }
    gbpchf_returns_series_2010 = gbpchf_trading(coint_results_2009_2010, prices)
    print(f'Returns in 2010: {round(sum(gbpchf_returns_series_2010) * 100, 2)}% \n')

    # No cointegration in 2011 - 2012

    # 2013 - 2014
    historical_spreads_2013 = full_range['uhat2_2013_2014'][1045:1305].tolist()
    trading_spreads_2014 = full_range['uhat2_2013_2014'][1305:1565].tolist()

    coint_results_2013_2014 = {
        'renormalised_beta_EURCHF': 1.0,
        'renormalised_beta_GBPCHF': -0.95383,
        'renormalised_beta_EURGBP': -1.6570,
        'historical_spreads': historical_spreads_2013,
        'trading_spreads': trading_spreads_2014
    }

    eurchf_bids, eurchf_asks = full_range['EURCHFClose_bid'][1305:1565], full_range['EURCHFClose_ask'][1305:1565]
    gbpchf_bids, gbpchf_asks = full_range['GBPCHFClose_bid'][1305:1565], full_range['GBPCHFClose_ask'][1305:1565]
    eurgbp_bids, eurgbp_asks = full_range['EURGBPClose_bid'][1305:1565], full_range['EURGBPClose_ask'][1305:1565]
    prices_2014 = {
        'eurchf_bids': eurchf_bids.tolist(), 'eurchf_asks': eurchf_asks.tolist(),
        'gbpchf_bids': gbpchf_bids.tolist(), 'gbpchf_asks': gbpchf_asks.tolist(),
        'eurgbp_bids': eurgbp_bids.tolist(), 'eurgbp_asks': eurgbp_asks.tolist()
    }
    gbpchf_returns_series_2014 = gbpchf_trading(coint_results_2013_2014, prices_2014)[1:]
    print(f'Returns in 2014: {round(sum(gbpchf_returns_series_2014) * 100, 2)}% \n')

    # 2015 - 2016
    historical_spreads_2015 = full_range['uhat2_2015_2016'][1570:1830].tolist()
    trading_spreads_2016 = full_range['uhat2_2015_2016'][1830:2090].tolist()

    coint_results_2015_2016 = {
        'renormalised_beta_EURCHF': 1.0,
        'renormalised_beta_GBPCHF': 1.1317,
        'renormalised_beta_EURGBP': 1.6573,
        'historical_spreads': historical_spreads_2015,
        'trading_spreads': trading_spreads_2016
    }

    eurchf_bids, eurchf_asks = full_range['EURCHFClose_bid'][1830:2090], full_range['EURCHFClose_ask'][1830:2090]
    gbpchf_bids, gbpchf_asks = full_range['GBPCHFClose_bid'][1830:2090], full_range['GBPCHFClose_ask'][1830:2090]
    eurgbp_bids, eurgbp_asks = full_range['EURGBPClose_bid'][1830:2090], full_range['EURGBPClose_ask'][1830:2090]
    prices_2016 = {
        'eurchf_bids': eurchf_bids.tolist(), 'eurchf_asks': eurchf_asks.tolist(),
        'gbpchf_bids': gbpchf_bids.tolist(), 'gbpchf_asks': gbpchf_asks.tolist(),
        'eurgbp_bids': eurgbp_bids.tolist(), 'eurgbp_asks': eurgbp_asks.tolist()
    }
    gbpchf_returns_series_2016 = gbpchf_trading(coint_results_2015_2016, prices_2016)
    print(f'Returns in 2016: {round(sum(gbpchf_returns_series_2016) * 100, 2)}% \n')

    # 2017 - 2018
    historical_spreads_2017 = full_range['uhat2_2017_2018'][2090:2350].tolist()
    trading_spreads_2018 = full_range['uhat2_2017_2018'][2350:2610].tolist()

    coint_results_2017_2018 = {
        'renormalised_beta_EURCHF': 1.0,
        'renormalised_beta_GBPCHF': -0.87899,
        'renormalised_beta_EURGBP': -1.2598,
        'historical_spreads': historical_spreads_2017,
        'trading_spreads': trading_spreads_2018
    }

    eurchf_bids, eurchf_asks = full_range['EURCHFClose_bid'][2350:2610], full_range['EURCHFClose_ask'][2350:2610]
    gbpchf_bids, gbpchf_asks = full_range['GBPCHFClose_bid'][2350:2610], full_range['GBPCHFClose_ask'][2350:2610]
    eurgbp_bids, eurgbp_asks = full_range['EURGBPClose_bid'][2350:2610], full_range['EURGBPClose_ask'][2350:2610]
    prices_2018 = {
        'eurchf_bids': eurchf_bids.tolist(), 'eurchf_asks': eurchf_asks.tolist(),
        'gbpchf_bids': gbpchf_bids.tolist(), 'gbpchf_asks': gbpchf_asks.tolist(),
        'eurgbp_bids': eurgbp_bids.tolist(), 'eurgbp_asks': eurgbp_asks.tolist()
    }
    gbpchf_returns_series_2018 = gbpchf_trading(coint_results_2017_2018, prices_2018)
    print(f'Returns in 2018: {round(sum(gbpchf_returns_series_2018) * 100, 2)}% \n')

    # No cointegration in 2019

