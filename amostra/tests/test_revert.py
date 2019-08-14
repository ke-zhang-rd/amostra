import amostra.mongo_client
from hypothesis import given, strategies as st
from hypothesis.strategies import text
from hypothesis import settings
from pymongo import MongoClient
import random
import uuid


alphabet_list = ''
for i in range(26):
    alphabet_list = alphabet_list + chr(97 + i)


@given(names = st.lists(st.text(alphabet=alphabet_list, min_size=1, max_size=4), min_size=3, max_size=4, unique=True))
@settings(max_examples = 10, deadline = 1000)
def test_revert(uid, names):
    print('uid',uid)
