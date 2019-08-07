import amostra.mongo_client
from hypothesis import given, strategies as st
from hypothesis.strategies import text
from hypothesis import settings
from pymongo import MongoClient

connection = MongoClient('localhost', 27017)
db = connection['tests-amostra']
collection = db['samples']
collection.drop()
collection = db['samples_revisions']
collection.drop()


client = amostra.mongo_client.Client('mongodb://localhost:27017/tests-amostra')


def test_one_plus_one_is_two():
    "Check that one and one are indeed two."
    assert 1 + 1 == 2

@given(st.lists(st.characters(whitelist_categories=['Lu']),
                              min_size=3,
                              max_size=6,
                              unique=True))

'''
Lu referece could be found here
https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
'''

def test_revert(names):
    print('names', names)
    n = len(names)
    s = client.samples.new(name = names[0])
    for name in names[1:]:
        s.name = name
    res = list(s.revisions())

    assert s.revision == n-1
    assert s.name == names[-1]
    if n > 1:
        for i in range(n-1):
            assert res[i].name == names[n-2-i]
    '''
    assert res[0].name == 'c'
    assert res[1].name == 'b'
    assert res[2].name == 'a'
    '''
    num = 1
    s.revert(num)
    res = list(s.revisions())

    assert s.revision == n
    assert s.name == names[n-2-num]
    if n > 1:
        for i in range(n):
            assert res[i].name== names[n-1-i]

    '''
    assert res[0].name == 'd'
    assert res[1].name == 'c'
    assert res[2].name == 'b'
    assert res[3].name == 'a'
    '''
