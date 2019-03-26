"""
FEATURES are the price changes for a day
LABEL will be whether or not we actually want to buy a specific company XYZ
For example, the label will be whether or not XYZ rose more than 2% within the next 7 days
https://www.quantinsti.com/blog/machine-learning-classification-strategy-python/
"""

import datetime
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.metrics import confusion_matrix, scorer, accuracy_score
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA
from sklearn.svm import LinearSVC, SVC
import Data as Data
import ConfigParameters as Cp


def prepare_data_for_machine_learning(predictor_tickers, response_ticker, train_test_crossover_date ='2017-01-01'):
    # Create df for factors
    df = Data.create_df_from_tickers(predictor_tickers + [response_ticker])
    #print(df.index[0])
    #print(df.index[-1])

    # Predictor variables (X)
    lag = 1
    predictor_columns = []
    for predictor_ticker in predictor_tickers:
        predictor_columns.append('Change_pct_{}'.format(predictor_ticker))

    X = df[predictor_columns].shift(lag)
    X = X[lag:]

    # Response variables (y): What I want to predict
    y = np.sign(df['Change_pct_' + response_ticker][lag:])     # 1 for pct_up and -1 for pct_down

    # Create training and test sets
    X_train = X[X.index < train_test_crossover_date]
    X_test = X[X.index >= train_test_crossover_date]
    y_train = y[y.index < train_test_crossover_date].values.ravel()
    y_test = y[y.index >= train_test_crossover_date].values.ravel()

    return X_train, X_test, y_train, y_test


def find_best_machine_learning_model(predictor_tickers, response_ticker, print_output=False):

    X_train, X_test, y_train, y_test = prepare_data_for_machine_learning(predictor_tickers, response_ticker)

    # Create the (parametrised) models
    models = [('LR', LogisticRegression()),
              ('LDA', LDA()),               # (Linear Discriminant Analysers)
              ('QDA', QDA()),               # (Quadratic Discriminant Analysers)
              ('LinearSVC', LinearSVC()),   # (Linear Support Vector Classifier)
              ('RSVM', SVC(                 # (Radial Support Vector Machine)
                  C=1000000.0, cache_size=200, class_weight=None,coef0=0.0, degree=3, gamma=0.0001, kernel='rbf',
                  max_iter=-1, probability=False, random_state=None, shrinking=True, tol=0.001, verbose=False)
               ),
              ('RF', RandomForestClassifier(    # (Random Forest)
                  n_estimators=1000, criterion='gini', max_depth=None, min_samples_split=2, min_samples_leaf=1,
                  max_features='auto', bootstrap=True, oob_score=False, n_jobs=1, random_state=None, verbose=0)
               )]

    results = {}
    # Iterate through the models
    for m in models:
        model_name = m[0]
        model = m[1]

        # Train each of the models on the training set
        cls = model.fit(X_train, y_train)

        # Output the hit-rate and the confusion matrix for each model
        hit_rate = model.score(X_test, y_test)

        if print_output is True:
            predictions = model.predict(X_test)      # Make an array of predictions on the test set
            print('\n{} hit rate = {}'.format(model_name, round(hit_rate, 2)))
            print('{}'.format(confusion_matrix(predictions, y_test)))

            accuracy_train = accuracy_score(y_train, cls.predict(X_train))
            accuracy_test = accuracy_score(y_test, cls.predict(X_test))

            print('\nTrain Accuracy:{: .2f}%'.format(accuracy_train * 100))
            print('Test Accuracy:{: .2f}%'.format(accuracy_test * 100))

        results[model_name] = hit_rate

    BestModel = max(results, key=results.get)

    if print_output is True:
        print('\n\nTicker: {}, BestModel: {}, HitRate: {}'.format(response_ticker, BestModel, results[BestModel]))

    return BestModel, results[BestModel]


def search():
    results = {}
    df = Data.get_ticker_metadata()
    df = df[df['Exchange_Sector'] == 'NASDAQ_Technology']
    universe_of_tickers = df.index.tolist()
    tickers = Data.get_tickers_with_good_data(universe_of_tickers)

    for ticker in tickers:
        try:
            predictor_tickers = ['NASDAQ:AAPL', 'NASDAQ:AMZN']    #   [Cp.ticker_benchmark]
            model, HitRate = find_best_machine_learning_model(predictor_tickers, ticker)
            results[ticker] = [model, HitRate]
            print({ticker: [model, HitRate]})
        except:
            print('Problem: {}'.format(ticker))
            pass

    df = pd.DataFrame.from_dict(results, orient='index')
    df.rename(columns={0: 'Model', 1: 'HitRate'}, inplace=True)
    print(df)
    df.to_csv(Cp.files['ML'])


def query_results():
    df = pd.read_csv(Cp.files['ML'])
    df = df[df['HitRate'] > 0.6]
    print(df)


if __name__ == "__main__":
    print('Start: {}\n'.format(datetime.datetime.today()))
    print(find_best_machine_learning_model(predictor_tickers=[Cp.ticker_benchmark, 'NASDAQ:AMAT'],
                                           response_ticker='NASDAQ:MU', print_output=True))
    # search()
    #query_results()
    print('\nFinished: {}'.format(datetime.datetime.today()))
