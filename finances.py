import numpy as np
import pandas as pd

def amortization(per, rate, pv,
    date=pd.to_datetime('today').strftime("%Y/%m/%d"), add=0):
    '''
    Returns two tables: monthly changes and summary over entire duration
    of loan.

    Parameters
    ----------
    per: scalar
        Number of total months.
    rate: scalar
        Percent annual interest rate.
    pv: scalar
        Principal amount loaned.
    date: string, optional
        Date entered as 'YYYYMMDD'.
    add: scalar, optional
        Additional payment towards principal given each month.

    Returns
    -------
    (df, sm) : (DataFrame, Series)
        df is a DataFrame with monthly breakdown of payments. sm is a Series
        table of summary of monthly over entire time of loan.

    Examples
    --------
    >>> import brindle as bd
    >>> import pandas as pd
    >>> df, sm = bd.amortization(72, 2.99, 35000, add=50)
    >>> pd.concat([df.head(2), df.tail(2)])
                 Date  Payment  Principal  Interest  Extra   Balance
        N
        0  2018-11-01     0.00       0.00      0.00      0  35000.00
        1  2018-12-01   581.62     492.74     88.88     50  34507.26
        65 2024-04-01   581.62     579.79      1.83     50    163.50
        66 2024-05-01   163.92     163.50      0.42     50      0.00

    >>> sm
        Payoff      2024-05-01 00:00:00
        Months                       66
        Rate                       2.99
        Payment                  531.62
        Extra                        50
        Interest                2969.22
        dtype: object

    >>> df1, sm1 = bd.amortization(72, 4.99, 22000, '20181026')
    >>> df2, sm2 = bd.amortization(72, 4.99, 22000, '20181026', add=100)
    >>> df3, sm3 = bd.amortization(72, 3.99, 22000, '20181026')
    >>> df4, sm4 = bd.amortization(72, 3.99, 22000, '20181026', add=50)
    >>> pd.DataFrame([sm, sm1, sm2, sm3])
              Payoff  Months  Rate  Payment  Extra  Interest
        0 2024-10-01      71  4.99   354.21      0   3504.11
        1 2023-06-01      55  4.99   354.21    100   2619.74
        2 2024-10-01      71  3.99   344.09      0   2775.79
        3 2024-01-01      62  3.99   344.09     50   2378.05
    '''
    # Generator to fill up DataFrame details.
    def calc(per, dates, pv, rate, pay, add, days):
        for i, (dt, dy) in enumerate(zip(dates, days)):
            if i == 0:
                yield dt, 0, 0, 0, 0, pv
            else:
                interest = round(pv * rate * dy / 100 / 365, 2)
                pr = min(pv, pay + add - interest)
                pv -= pr
                yield dt, pr + interest, pr, interest, add, pv
            if pv <= 0: break

    # Create time series DataFrame table of loan details.
    dates = pd.date_range(date, periods=per+1, freq='MS')
    days = np.array(np.array(np.diff(dates), dtype='timedelta64[D]'), dtype=int)
    pay = round(-np.pmt(rate / 100 / 12, per, pv), 2)
    cols = ['Date', 'Payment', 'Principal', 'Interest', 'Extra', 'Balance']
    df = pd.DataFrame(list(calc(per, dates, pv, rate, pay, add, days)),
        columns=cols)
    df.index.name = 'N'

    # Create summary table of loan details.
    index = ['Payoff', 'Months', 'Rate', 'Payment', 'Extra', 'Interest']
    sm = pd.Series([df['Date'].iloc[-1], len(df) - 1, rate, pay, add,
        np.sum(df['Interest'])], index=index)
    return df, sm
