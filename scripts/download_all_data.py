from argparse import ArgumentParser
from pathlib import Path
import json
import os

from more_itertools import chunked
import tqdm
import tweepy


def connect_to_api(auth_json_path: str) -> tweepy.API:
    with open(auth_json_path, 'r', encoding='utf-8') as f:
        auth_json = json.load(f)

    auth = tweepy.OAuthHandler(auth_json['ConsumerKey'], auth_json['ConsumerSecret'])
    auth.set_access_token(auth_json['AccessKey'], auth_json['AccessSecret'])

    return tweepy.API(auth, wait_on_rate_limit=True)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('id_files', nargs='+',
                        help='list of paths to files containing tweet ids, following special naming format')
    parser.add_argument('output', help='path for the output JSON file')
    parser.add_argument('--auth', help='path to JSON file containing auth keys')
    parser.add_argument('--skipped_log', help='path to txt file containing tweet ids which were skipped')
    parser.add_argument('--tolerance', type=int, default=5,
                        help='if exception happens n times in a row, execution is terminated')
    parser.add_argument('--save_every', type=int, default=None, help='save every n requests')
    parser.add_argument('--processed_ids', help='path to txt file containing processed tweet ids to skip')
    args = parser.parse_args()

    output = Path(args.output).resolve()

    if os.path.exists(args.processed_ids):
        with open(args.processed_ids, 'r', encoding='utf-8') as f:
            previously_processed_ids = set([line.strip() for line in f.read().strip('\n').split('\n')])
    else:
        previously_processed_ids = set()

    api = connect_to_api(args.auth)

    processed_ids = []
    tweets = []
    steps = 0
    exceptions = 0
    for filepath in args.id_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            ids = [
                line.strip()
                for line in f.read().strip('\n').split('\n')
                if line.strip() not in previously_processed_ids
            ]

        for tweet_ids in tqdm.tqdm(list(chunked(ids, n=100, strict=False)), desc=f'processing {filepath}'):
            try:
                response = api.lookup_statuses(tweet_ids, tweet_mode='extended', map=True)
            except tweepy.errors.TweepyException as ex:
                exceptions += 1

                with open(args.skipped_log, 'a+', encoding='utf-8') as f:
                    f.write('\n'.join(tweet_ids) + '\n')

                if exceptions >= args.tolerance:
                    raise RuntimeError('tolerance exceeded') from ex

                continue

            exceptions = 0
            processed_ids.extend(tweet_ids)
            tweets.extend([tweet._json for tweet in response])

            steps += 1
            if args.save_every and steps >= args.save_every:
                with output.open('a+', encoding='utf-8') as f:
                    f.write('\n'.join([json.dumps(tweet, ensure_ascii=False) for tweet in tweets]) + '\n')
                with open(args.processed_ids, 'a+', encoding='utf-8') as f:
                    f.write('\n'.join(processed_ids) + '\n')
                steps = 0
                tweets = []
                processed_ids = []

    with output.open('a+', encoding='utf-8') as f:
        f.write('\n'.join([json.dumps(tweet, ensure_ascii=False) for tweet in tweets]) + '\n')

    with open(args.processed_ids, 'a+', encoding='utf-8') as f:
        f.write('\n'.join(processed_ids) + '\n')
