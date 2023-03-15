from argparse import ArgumentParser
from typing import Optional
import json

from pymongo import MongoClient
from pprint import pprint


def connect_to_db(host: str, port: int, username: str, password: str) -> MongoClient:
    client = MongoClient(
        host=host,
        port=port,
        username=username,
        password=password
    )
    return client


def process_line(line: str) -> Optional[dict]:
    data = json.loads(line)

    if 'created_at' not in data:
        return None

    processed = {
        'created_at': data['created_at'],
        # 'entities': data['entities'],
        'full_text': data['full_text'],
        'geo': data['geo'],
        'id': data['id_str'],
        'lang': data['lang'],
        'retweet_count': data['retweet_count'],
        # 'user': data['user']
    }

    return processed


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input', help='input file, where each line is a tweet JSON')
    parser.add_argument('--host', help='MongoDB host')
    parser.add_argument('--port', type=int, help='MongoDB port')
    parser.add_argument('--username', help='MongoDB username')
    parser.add_argument('--password', help='MongoDB password')
    parser.add_argument('--db', help='database name')
    parser.add_argument('--collection', help='collection name')
    parser.add_argument('--batch', default=50, type=int, help='batch size (inserting multiple tweets at the same time)')
    args = parser.parse_args()

    client = connect_to_db(args.host, args.port, args.username, args.password)
    db = client[args.db]
    collection = db[args.collection]

    items = []
    with open(args.input, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            item = process_line(line)
            if item:
                items.append(item)

            if len(items) >= args.batch:
                collection.insert_many(items)  # TODO process result?
                items = []

    # if any tweets left
    if items:
        collection.insert_many(items)
