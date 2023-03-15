import os

# from dotenv import load_dotenv
from pyspark.sql import SparkSession


# load_dotenv('.env')


# .config("spark.mongodb.read.connection.uri", "mongodb://127.0.0.1/") \
#     .config("spark.mongodb.read.database", "tweets") \
#     .config("spark.mongodb.read.collection", "tweets") \



spark = SparkSession.builder \
    .appName('twitter') \
    .master('local[*]') \
    .config("spark.mongodb.read.connection.uri", "mongodb://admin:pass@127.0.0.1/tweets.tweets?authSource=admin") \
    .config("spark.mongodb.write.connection.uri", "mongodb://admin:pass@127.0.0.1/tweets.tweets?authSource=admin") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
    .getOrCreate()
