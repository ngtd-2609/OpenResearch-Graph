from app.services.openalex_service import OpenAlexService,reconstruct_abstract

def test_reconstruct_abstract():
    assert reconstruct_abstract({"world":[1],"hello":[0]})=="hello world"

def test_normalize_minimal_work():
    item={"id":"https://openalex.org/W1","display_name":"Paper","publication_year":2025,"cited_by_count":2}
    normalized=OpenAlexService.normalize_work(item)
    assert normalized["title"]=="Paper"
    assert normalized["openalex_id"].endswith("W1")
