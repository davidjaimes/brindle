def amortization(rate, per, pv, date, st=0, add=0):
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

    cols = ['Date', 'Rate', 'Months', 'Interest', 'Principal', 'Additional']
    summ = pd.Series(data=[df['Date'].iloc[-1], rate, len(df)-1,
        np.sum(df['Interest']), np.sum(df['Principal']),
        np.sum(df['Additional'])], index=cols)
    return df, summ
