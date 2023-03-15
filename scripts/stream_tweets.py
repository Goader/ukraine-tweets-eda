from argparse import ArgumentParser
import json

import tweepy


def connect_to_api(auth_json_path: str) -> tweepy.API:
    with open(auth_json_path, 'r', encoding='utf-8') as f:
        auth_json = json.load(f)

    auth = tweepy.OAuthHandler(auth_json['ConsumerKey'], auth_json['ConsumerSecret'])
    auth.set_access_token(auth_json['AccessKey'], auth_json['AccessSecret'])

    return tweepy.API(auth, wait_on_rate_limit=True)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--auth', help='path to JSON file containing auth keys')
    args = parser.parse_args()

    api = connect_to_api(args.auth)

    # TODO
