def amortization(rate, per, pv, date, st=(15, 'D'), add=0):
    '''
    Returns two tables: monthly changes and summary over entire duration
    of loan.

    Parameters
    ----------
    rate: scalar
        Percent annual interest rate.
    per: scalar
        Number of total compounding periods.
    pv: scalar
        Principal amount loaned.
    date: string
        Date entered as 'YYYYMMDD'.
    st: tuple, optional
        Shift in days starting from beginning of month.
    add: scalar
        Additional payment towards principal given each month.

    Returns
    -------
    (df, sm) : (DataFrame, Series)
        df is a DataFrame with monthly breakdown of payments. summ is a Series
        table of summary of monthly over entire time of loan.

    Examples
    --------
    >>> import brindle as bd
    >>> df, sm = bd.amortization(2.99, 72, 35000, '20181025')
    >>> df.head()
                Date    Start Interest Principal Additional      End
        N
        0 2018-10-25    35000        0         0          0    35000
        1 2018-11-16    35000    63.08    468.54          0  34531.5
        2 2018-12-16  34531.5    86.01    445.61          0  34085.8
        3 2019-01-16  34085.8    87.69    443.93          0  33641.9
        4 2019-02-16  33641.9    86.56    445.06          0  33196.9

    >>> sm
        Date          2024-10-16 00:00:00
        Rate                         2.99
        Months                         72
        Payment                    531.62
        Interest                  3342.31
        Principal                 34934.3
        Additional                      0
        dtype: object

    >>> df1, sm1 = bd.amortization(2.99, 72, 35000, '20181025', add=100)
    >>> df2, sm2 = bd.amortization(1.50, 72, 35000, '20181025')
    >>> df3, sm3 = bd.amortization(1.50, 72, 35000, '20181025', add=50)
    >>> pd.DataFrame([sm, sm1, sm2, sm3])
                Date  Rate  Months  Payment  Interest  Principal  Additional
        0 2024-10-16  2.99      72   531.62   3342.31   34934.33           0
        1 2023-09-16  2.99      59   531.62   2773.52   28592.06        5900
        2 2024-10-16  1.50      72   508.62   1652.64   34968.00           0
        3 2024-03-16  1.50      65   508.62   1500.92   31559.38        3250
    '''
    import numpy as np
    import pandas as pd

    pay =  -round(np.pmt(rate/100/12, per, pv), 2)
    cols = ['Date', 'Start', 'Interest', 'Principal', 'Additional', 'End']
    df = pd.DataFrame(index=np.arange(per+1), columns=cols)
    df.index.name = 'N'

    dt = pd.date_range(date, periods=per, freq='MS').shift(*st)
    dt = dt.insert(0, pd.to_datetime(date))
    df.iloc[0] = [0, pv, 0, 0, 0, pv]

    days = np.array(np.diff(dt), dtype='timedelta64[D]')
    days = np.array(days, dtype=int)
    for i, d in enumerate(days):
        df['Start'][i+1] = df['End'][i]
        df['Interest'][i+1] = round(df['Start'][i] * d * rate / 100 / 365, 2)
        df['Principal'][i+1] = pay - df['Interest'][i+1]
        df['Additional'][i+1] = add
        df['End'][i+1] = (df['Start'][i+1] - df['Principal'][i+1] -
            df['Additional'][i+1])
    df = df[df['End'] >= 0]
    df['Date'] = dt[:len(df)]

    cols = ['Date', 'Rate', 'Months', 'Payment', 'Interest', 'Principal', 'Additional']
    sm = pd.Series(data=[df['Date'].iloc[-1], rate, len(df)-1, pay,
        np.sum(df['Interest']), np.sum(df['Principal']),
        np.sum(df['Additional'])], index=cols)
    return df, sm
