import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from extensions.general.info import InfoCog


def test_create_embed_contains_stable_project_info_and_uptime(monkeypatch):
    monkeypatch.setattr("extensions.general.info.time.monotonic", lambda: 3_661)
    cog = InfoCog(SimpleNamespace(color=0xFF3351, started_at=0))
    embed = cog.create_embed()

    assert InfoCog.info.description == "Learn about Sakamoto and check its uptime."
    assert embed.title == ":information_source: About Sakamoto"
    assert (
        embed.description
        == "A voice-first Discord bot for small-to-medium communities."
    )
    assert embed.color.value == 0xFF3351
    assert [(field.name, field.value, field.inline) for field in embed.fields] == [
        ("Uptime", "1h 1m", True),
        ("Project", "[GitHub](https://github.com/taichikuji/Sakamoto)", True),
    ]


def test_uptime_formats_hours_and_remaining_minutes(monkeypatch):
    monkeypatch.setattr("extensions.general.info.time.monotonic", lambda: 3_661)

    assert InfoCog(SimpleNamespace(started_at=0)).uptime() == "1h 1m"
