import amostra.mongo_client
from hypothesis import given, strategies as st
from hypothesis.strategies import text, dictionaries
from hypothesis import settings
from pymongo import MongoClient
import random
import hypothesis_jsonschema

from amostra.utils import load_schema
connection = MongoClient('localhost', 27017)
db = connection['tests-amostra']
db['samples'].drop()
db['samples_revisions'].drop()


client = amostra.mongo_client.Client('mongodb://localhost:27017/tests-amostra')

d = load_schema('sample.json')
st_sample = hypothesis_jsonschema.from_schema(d)


@given(st.lists(st_sample, unique_by = lambda x: x['name'], min_size = 3, max_size=5))
@settings(max_examples=1)
def test_new(samples_stream):
    print(len(samples_stream))
    print(samples_stream)
