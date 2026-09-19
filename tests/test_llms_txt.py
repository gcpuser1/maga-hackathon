from pathlib import Path
import re

ROOT = Path(__file__).parent.parent


def test_every_relative_link_in_llms_txt_resolves() -> None:
    links = re.findall(r"\]\(([^)]+)\)", (ROOT / "llms.txt").read_text())
    local = [link for link in links if not link.startswith("http")]
    assert local, "llms.txt has no local links, so this test checks nothing"
    assert [link for link in local if not (ROOT / link).exists()] == []
