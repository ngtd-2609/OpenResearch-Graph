from app.ml.evaluation.recommendation_metrics import ndcg_at_k,precision_at_k,recall_at_k

def test_ranking_metrics():
    recommended=["a","b","c"]; relevant={"a","c"}
    assert precision_at_k(recommended,relevant,2)==0.5
    assert recall_at_k(recommended,relevant,3)==1
    assert 0<ndcg_at_k(recommended,relevant,3)<=1
