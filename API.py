from yahoo_finance import Share
import quandl
import ConfigParameters as Cp


def yahoo_example():
    ticker = Share('YHOO')
    print(ticker.get_price())


def quandl_example():
    quandl.ApiConfig.api_key = Cp.quandl_key
    # data = quandl.get_table('MER/F1', compnumber="39102", paginate=True)
    # print(data[['indicator', 'amount']])
    data = quandl.get_table('SHARADAR', paginate=True)


if __name__ == '__main__':
    quandl_example()