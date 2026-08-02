import math

def test_normalized_popularity_is_bounded():
    score = math.log1p(100) / math.log1p(1000)
    assert 0 < score < 1
