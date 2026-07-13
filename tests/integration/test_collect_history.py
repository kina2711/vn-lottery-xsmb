from pathlib import Path

from vn_lottery_xsmb.parser.html_parser import LotteryHtmlParser
from vn_lottery_xsmb.parser.normalizer import normalize_draw
from vn_lottery_xsmb.storage.csv_store import CsvStore
from vn_lottery_xsmb.storage.models import SourceRecord
from vn_lottery_xsmb.storage.repository import LotteryRepository


def test_collect_pipeline_stores_once() -> None:
    html = Path("tests/fixtures/draw_valid.html").read_text(encoding="utf-8")
    raw = LotteryHtmlParser().parse(html)
    draw = normalize_draw(
        raw,
        SourceRecord(source_name="fixture", source_url="https://example.test/2026-07-13"),
    )
    store = CsvStore(
        Path(".test-output/integration/draws.csv"),
        Path(".test-output/integration/prizes.csv"),
    )
    repository = LotteryRepository(store)

    first = repository.save_draws([draw])
    second = repository.save_draws([draw])

    assert first.added + first.unchanged == 1
    assert second.unchanged == 1
    assert len(store.load_draws()) == 1
