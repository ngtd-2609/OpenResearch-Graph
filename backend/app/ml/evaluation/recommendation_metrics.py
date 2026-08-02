from collections.abc import Iterable

def precision_at_k(recommended: list[str], relevant: set[str], k: int) -> float:
    chosen = recommended[:k]
    return len(set(chosen) & relevant) / max(k, 1)

def recall_at_k(recommended: list[str], relevant: set[str], k: int) -> float:
    return len(set(recommended[:k]) & relevant) / max(len(relevant), 1)

def ndcg_at_k(recommended: list[str], relevant: set[str], k: int) -> float:
    import math
    dcg=sum((1.0 if item in relevant else 0.0)/math.log2(index+2) for index,item in enumerate(recommended[:k]))
    ideal=sum(1.0/math.log2(index+2) for index in range(min(k,len(relevant))))
    return dcg/ideal if ideal else 0.0

def coverage(all_recommended: Iterable[str], catalog: set[str]) -> float:
    return len(set(all_recommended))/max(len(catalog),1)
