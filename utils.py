# utils.py

# Utilities for all strategies

from statistics import mean, stdev


def historical_crossings(historical_spreads):
    """ Computes the number of historical crossings.

        :param: data is a list
        :returns: number of historical crossings -> int
    """
    mean_of_spread = mean(historical_spreads)
    st_dev_of_spread = stdev(historical_spreads)
    n = len(historical_spreads)
    hist_crossings = 0

    for i in range(1, n):  # i = tomorrow, i - 1 = today
        # compute difference in absolute terms to capture differences between +/- values of the
        # residuals and the historical standard deviation of the spread
        current_spread = historical_spreads[i - 1]
        next_spread = historical_spreads[i]
        distance_from_st_dev_of_current_spread = abs(current_spread) - abs(st_dev_of_spread)
        if distance_from_st_dev_of_current_spread > 0:  # deviation greater than 1 standard deviation so open trade
            # Simple approach is to compute distance between previous spread and next spread and if the
            # distance between the two is greater than the distance between previous spread and the mean,
            # then the next period crossed the mean so we have a mean reversion between current spread and next one:
            bigger_spread = max(next_spread, current_spread)
            smaller_spread = min(next_spread, current_spread)
            diff = bigger_spread - smaller_spread
            bigger_spread_current_from_mean = max(current_spread, mean_of_spread)
            smaller_spread_current_from_mean = min(current_spread, mean_of_spread)
            diff_current_spread_from_mean = bigger_spread_current_from_mean - smaller_spread_current_from_mean
            if diff > diff_current_spread_from_mean:  # we had a crossing
                hist_crossings += 1

    return hist_crossings

def returns_calculation(data):
    """ Compute the daily returns of the cointegrated combination using formula in model paper.

        :param: data is a list of either two or three cointegrated assets
        :return: the return in percentage
    """
    daily_return = 0
    n = len(data)
    for i in range(n):
        asset_i_return = 0
        I = data[i]['I']  # returns either 0 = not invested, 1 = long, -1 = short
        price_t = data[i]['current_close']
        price_t_1 = data[i]['previous_close']
        # the cointegration weight is the beta from the cointegrating regression
        cointegration_weight = abs(data[i]['cointegration_weight'])
        weighted_sum = 0
        for j in range(n):
            weighted_sum += data[j]['previous_close'] * abs(data[j]['cointegration_weight'])

        # value-weighted return
        asset_i_return += I * ((price_t / price_t_1) - 1) * ((price_t_1 * cointegration_weight) / weighted_sum)
        # simple return, assuming uniform amounts either bought or sold
        # asset_i_return += I * ((price_t / price_t_1) - 1)
        daily_return += asset_i_return

    return daily_return

def sharpe_ratio(portfolio_returns, risk_free_rate, standard_deviation_portfolio_returns):
    """ Compute Sharpe ratio of a given portfolio. """
    sharpe = (portfolio_returns - risk_free_rate) / standard_deviation_portfolio_returns
    return sharpe

if __name__ == '__main__':
    import pandas as pd

    data = pd.read_csv('data.csv')
    data = data[7:129]  # 01/01/2009 - 30/06/2009

    eurchf_crossings = historical_crossings(data['uhat1_2009_2010'].tolist())
    print(f"Historical crossings of EUR/CHF: {eurchf_crossings}")
    gbpchf_crossings = historical_crossings(data['uhat2_2009_2010'].tolist())
    print(f"Historical crossings of GBP/CHF: {gbpchf_crossings}")
    eurgbp_crossings = historical_crossings(data['uhat3_2009_2010'].tolist())
    print(f"Historical crossings of EUR/GBP: {eurgbp_crossings}")