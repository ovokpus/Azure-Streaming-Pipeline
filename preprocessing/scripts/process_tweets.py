from pathlib import Path
import itertools
import pandas as pd
import json

# load and shuffle data
twitter_data_filepath = "./preprocessing/data/original/hurricane_harvey.csv"


def read_preprocess_twitter_data(twitter_data_filepath):
    '''Reads and preprocesses twitter data
    Returns:
        df (pandas.DataFrame): Dataframe containing twitter data
    '''
    tweets_df = (pd.read_csv(twitter_data_filepath, encoding="latin-1")
                 .drop(labels=['Unnamed: 0'], axis="columns")
                 .dropna()
                 .drop(['ID'], axis="columns")
                 .sample(frac=1).reset_index(drop=True)
                 )

    tweets_df = tweets_df.assign(
        Time=pd.to_datetime(tweets_df['Time']),
    )

    tweets_df = tweets_df.assign(
        Year=tweets_df['Time'].dt.year,
        Month=tweets_df['Time'].dt.month,
        Day=tweets_df['Time'].dt.day
    )

    tweets_df = tweets_df.assign(
        YearMonthDay=tweets_df['Time'].dt.strftime('%Y-%m-%d')
    )
    print("columns of tweet_df", tweets_df.columns)
    return tweets_df


def create_artificial_ids(group_size, df):
    '''Creates artificial ids for tweets from the rowcounts and group choice
    Args:
        group_size (int): Size of each group
        df (pandas.DataFrame): Dataframe containing twitter data
    Returns:
        ids (int): Artificial ids for tweets
    '''
    # split to groups
    number_of_groups = len(df) // group_size
    remainder = len(df) % group_size
    assert (number_of_groups * group_size + remainder) == len(df)

    # create artificial ids
    twitter_accounts = []
    for id in range(1, number_of_groups + 1):
        twitter_accounts.append(
            [num for num in itertools.repeat(id, group_size)])

    for id in range(number_of_groups, remainder + 1):
        twitter_accounts.append(
            [num for num in itertools.repeat(id, remainder)])

    remainder_ids = [num for num in itertools.repeat(
        number_of_groups + 1, remainder)]

    twitter_accounts.append(remainder_ids)

    # flatten list of lists
    flattened_ids = []
    for sublist in twitter_accounts:
        for item in sublist:
            flattened_ids.append(item)

    return flattened_ids


def assign_id_columns(tweets_df, group_size, df):
    '''
    Assigns ids to columns in dataframe
    '''
    tweets_df["account_id"] = create_artificial_ids(group_size, df)
    tweets_df["tweet_id"] = range(len(tweets_df))

    # tweets_df.columns = ['likes', 'replies' 'retweets', 'time', 'year', 'month',
    #                      'day', 'year_month_day', 'account_id', 'tweet_id']
    column_names = ['account_id', 'tweet_id', 'Time', 'Replies',
                    'YearMonthDay', 'Likes', 'Tweet', 'Retweets']

    tweets_df = tweets_df[column_names]
    tweets_df = tweets_df.rename(columns={'Replies': 'replies', 'Likes': 'likes',
                                          'Tweet': 'tweet', 'Retweets': 'retweets',
                                 'Time': 'time', 'YearMonthDay': 'year_month_day'
                                          }
                                 )
    print("returning tweets_df, columns:", tweets_df.columns)
    tweets_df.to_csv(
        "./preprocessing/data/preprocessed/tweets_df.csv", index=False)
    return tweets_df


def split_to_batch_and_streaming_data(tweets_df):
    '''
    Splits data to batch and streaming data
    '''
    tweets_stream = ['2017-08-25']

    tweets_batch = ['2017-08-26', '2017-08-27', '2017-08-24', '2017-08-28',
                    '2017-08-29', '2017-08-23', '2017-06-01', '2017-06-21', '2017-08-17',
                    '2017-08-18', '2017-08-14', '2017-08-22', '2017-02-19', '2017-03-28',
                    '2017-08-19', '2017-08-13', '2017-05-21', '2017-05-26', '2017-04-19',
                    '2017-08-16', '2017-08-15', '2017-06-09', '2017-08-21', '2017-06-02',
                    '2017-02-21', '2017-05-25', '2017-04-20', '2017-08-04', '2017-03-21',
                    '2017-08-20', '2017-01-11', '2017-02-10']

    tweets_stream = tweets_df.query("year_month_day in @tweets_stream")
    tweets_batch = tweets_df.query("year_month_day in @tweets_batch")

    tweets_stream.to_csv(
        "./preprocessing/data/preprocessed/stream/tweets_stream.csv", index="False")
    print("steaming data saved to csv")

    (tweets_batch
        .groupby("year_month_day")
        .apply(
            lambda x: x.to_csv(
                f"./preprocessing/data/preprocessed/batch/{x.name}.csv", index=False)
        )
     )
    print("batch data saved to csv")

    tweets_stream.to_json(
        "./preprocessing/data/preprocessed/stream/tweets_stream.json", orient="records")
    print("steaming data saved to json")

    return tweets_stream


if __name__ == "__main__":
    tweets_df = read_preprocess_twitter_data(twitter_data_filepath)
    flattened_ids = create_artificial_ids(group_size=100, df=tweets_df)
    tweets_df = assign_id_columns(tweets_df, group_size=100, df=tweets_df)
    tweets_stream = split_to_batch_and_streaming_data(tweets_df)
    tweets_stream.to_json(
        "./preprocessing/data/preprocessed/stream/tweets_stream.json", orient="records")
    print("steaming data saved to json -- again!?")
