import os

import pytest

from httpie import downloads


pytestmark = pytest.mark.skipif(
    os.name != 'nt', reason='Windows character-count filename fallback'
)


@pytest.mark.parametrize('filename, expected', [
    ('\u732b' * 4 + '.txt', '\u732b' * 4 + '.txt'),
    ('\u732b' * 8 + '.txt', '\u732b' * 6 + '.txt'),
    ('x.' + '\u732b' * 12, 'x.' + '\u732b' * 8),
    ('\u00e9' * 8 + '.\u732b', '\u00e9' * 8 + '.\u732b'),
])
def test_windows_filename_character_budget(monkeypatch, filename, expected):
    monkeypatch.setattr(downloads, 'get_filename_max_length', lambda _: 10)
    assert downloads.get_unique_filename(filename, exists=lambda _: False) == expected


def test_windows_filename_collision_can_be_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(downloads, 'get_filename_max_length', lambda _: 10)
    original = '\u732b' * 6 + '.txt'
    expected = ('\u732b' * 6 + '.txt', '\u732b' * 4 + '.txt-1')
    for attempt, expected_name in enumerate(expected):
        filename = downloads.get_unique_filename(original)
        assert filename == expected_name
        assert len(filename) == 10
        payload = str(attempt).encode('ascii')
        path = tmp_path / filename
        with path.open('xb') as output:
            output.write(payload)
        assert path.read_bytes() == payload
    assert {path.name for path in tmp_path.iterdir()} == set(expected)
