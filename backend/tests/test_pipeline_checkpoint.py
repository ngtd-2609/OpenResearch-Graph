from pathlib import Path

from data_pipeline.ingestion.common import PipelineCheckpoint
from data_pipeline.ingestion.snapshot import iter_snapshot_files, open_text


def test_checkpoint_round_trip_is_atomic(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "checkpoint.json"
    expected = PipelineCheckpoint(
        source="sample.jsonl",
        position=12,
        processed=10,
        errors=2,
        cursor="next",
    )
    expected.save(path)

    assert PipelineCheckpoint.load(path) == expected
    assert not path.with_suffix(".json.tmp").exists()


def test_snapshot_file_discovery_is_sorted_and_filtered(tmp_path: Path) -> None:
    (tmp_path / "b.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "a.gz").write_bytes(b"")
    (tmp_path / "ignore.txt").write_text("skip", encoding="utf-8")

    names = [item.name for item in iter_snapshot_files(tmp_path)]
    assert names == ["a.gz", "b.jsonl"]


def test_open_text_supports_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "sample.jsonl"
    path.write_text('{"id": "W1"}\n', encoding="utf-8")
    with open_text(path) as stream:
        assert stream.readline().startswith('{"id"')
