import os.path
import sys

import pandas as pd

if __name__ == '__main__':

    # Print usage
    if len(sys.argv) < 3:
        print('usage: {} [steam_full_dir] [users_csv]'.format(sys.argv[0]))
        exit(1)

    # Parse arguments
    users_csv = sys.argv[2]
    steam_full_dir = sys.argv[1]
    steam_sample_dir = os.path.dirname(users_csv)

    # CSV files
    app_full = steam_full_dir + 'App_ID_Info.csv'
    dev_full = steam_full_dir + 'Games_Developers.csv'
    pub_full = steam_full_dir + 'Games_Publishers.csv'
    game_full = steam_full_dir + 'Games_2.csv'
    genre_full = steam_full_dir + 'Games_Genres.csv'

    # Sampled CSV files
    app_csv = steam_sample_dir + '/apps.csv'
    game_csv = steam_sample_dir + '/games.csv'

    # Load users
    print('Loading {} ...'.format(users_csv))
    users = set()
    with open(users_csv, 'r') as f:
        for line in f:
            user_id = line.split(',')[0]
            users.add(user_id)
    
    # Sampling games
    print('Sampling {} ...'.format(game_csv))
    apps = set()
    game_file = open(game_csv, 'w')
    with open(game_full, 'r') as f:
        f.readline()
        for line in f:
            fields = line.split(',')
            user_id = fields[0]
            app_id = fields[1]
            # Sampled user
            if user_id in users:
                apps.add(app_id)
                game_file.write(line)
            
    # Sampling apps
    print('Sampling {} ...'.format(app_csv))
    app_file = open(app_csv, 'w')
    with open(app_full, 'r') as f:
        f.readline()
        for line in f:
            app_id = line.split(',')[0]
            # Sampled app
            if app_id in apps:
                app_file.write(line)

    # Add genres
    print('Adding generes to {} ...'.format(app_csv))
    app_df = pd.read_csv(app_csv, quotechar="'", escapechar='\\',
        names=['appid','Title','Type','Price','Release_Date','Rating','Required_Age','Is_Multiplayer'])
    generes_df = pd.read_csv(genre_full, quotechar="'", escapechar='\\')
    generes_df = generes_df.groupby('appid').agg(lambda col: '|'.join(col))
    generes_df.reset_index(inplace=True)
    app_df = pd.merge(app_df, generes_df, how='left')

    # Add publishers
    print('Adding publishers to {} ...'.format(app_csv))
    publishers_df = pd.read_csv(pub_full, quotechar="'", escapechar='\\')
    publishers_df = publishers_df.groupby('appid').agg(lambda col: '|'.join(col))
    publishers_df.reset_index(inplace=True)
    app_df = pd.merge(app_df, publishers_df, how='left')

    # Add developers
    print('Adding developers to {} ...'.format(app_csv))
    developers_df = pd.read_csv(dev_full, quotechar="'", escapechar='\\')
    developers_df = developers_df.groupby('appid').agg(lambda col: '|'.join(col))
    developers_df.reset_index(inplace=True)
    app_df = pd.merge(app_df, developers_df, how='left')
    app_df.to_csv(app_csv, index=False)
