import amostra.mongo_client
from hypothesis import given, strategies as st
from hypothesis.strategies import text
from hypothesis import settings
from pymongo import MongoClient
import random

connection = MongoClient('localhost', 27017)
db = connection['tests-amostra']
db['samples'].drop()
db['samples_revisions'].drop()


client = amostra.mongo_client.Client('mongodb://localhost:27017/tests-amostra')


def test_one_plus_one_is_two():
    "Check that one and one are indeed two."
    assert 1 + 1 == 2

alphabet_list = ''
for i in range(26):
    alphabet_list = alphabet_list + chr(97 + i)

@given(st.lists(st.text(alphabet=alphabet_list, min_size=1, max_size=4),
                min_size=2,
                max_size=4,
                unique=True))
def test_revert(names):
    print('random names', names)
    n = len(names)
    s = client.samples.new(name = names[0])
    for name in names[1:]:
        s.name = name
    res = list(s.revisions())

    assert s.revision == n-1
    assert s.name == names[-1]
    for i in range(n-1):
        assert res[i].name == names[n-2-i]
    '''
    assert res[0].name == 'c'
    assert res[1].name == 'b'
    assert res[2].name == 'a'
    '''
    num = random.randint(0, n-2)
    s.revert(num)
    res = list(s.revisions())

    assert s.revision == n
    assert s.name == names[n-2-num]
    for i in range(n):
        assert res[i].name== names[n-1-i]

    '''
    assert res[0].name == 'd'
    assert res[1].name == 'c'
    assert res[2].name == 'b'
    assert res[3].name == 'a'
    '''
