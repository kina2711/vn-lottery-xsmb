from pathlib import Path

from vn_lottery_xsmb.parser.html_parser import LotteryHtmlParser
from vn_lottery_xsmb.parser.normalizer import normalize_draw
from vn_lottery_xsmb.storage.csv_store import CsvStore
from vn_lottery_xsmb.storage.models import SourceRecord
from vn_lottery_xsmb.storage.repository import StorageAction


def _draw():
    html = Path("tests/fixtures/draw_valid.html").read_text(encoding="utf-8")
    raw = LotteryHtmlParser().parse(html)
    return normalize_draw(
        raw,
        SourceRecord(source_name="fixture", source_url="https://example.test/2026-07-13"),
    )


def test_csv_store_upsert_prevents_duplicates() -> None:
    store = CsvStore(Path(".test-output/store/draws.csv"), Path(".test-output/store/prizes.csv"))
    draw = _draw()

    first = store.upsert(draw)
    second = store.upsert(draw)

    assert first.action in {StorageAction.ADDED, StorageAction.UNCHANGED}
    assert second.action == StorageAction.UNCHANGED
    assert len(store.load_draws().loc[lambda frame: frame["draw_date"] == "2026-07-13"]) == 1
