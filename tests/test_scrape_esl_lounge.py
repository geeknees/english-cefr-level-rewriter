# ABOUTME: Tests for ESL Lounge scraper — parsing and URL construction
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "english-cefr-level-rewriter" / "scripts"))

from scrape_esl_lounge import build_url, fetch_words, write_csv


def test_build_url():
    assert build_url("a1", "nouns") == (
        "https://www.esl-lounge.com/student/reference/"
        "a1-cefr-vocabulary-word-list-nouns.php"
    )


def test_build_url_b2_verbs():
    assert build_url("b2", "verbs") == (
        "https://www.esl-lounge.com/student/reference/"
        "b2-cefr-vocabulary-word-list-verbs.php"
    )


def _mock_response(html: str) -> MagicMock:
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_fetch_words_parses_table():
    html = """
    <html><body>
    <table>
      <tr><td>apple</td><td>I eat an apple.</td><td>/ˈæp.əl/</td></tr>
      <tr><td>book</td><td>Read this book.</td><td>/bʊk/</td></tr>
    </table>
    </body></html>
    """
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "apple" in words
    assert "book" in words


def test_fetch_words_lowercases():
    html = "<html><body><table><tr><td>Apple</td><td>ex</td><td>ipa</td></tr></table></body></html>"
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "apple" in words
    assert "Apple" not in words


def test_fetch_words_skips_empty_first_cell():
    html = """
    <html><body><table>
      <tr><td></td><td>empty</td><td>ipa</td></tr>
      <tr><td>cat</td><td>The cat sat.</td><td>/kæt/</td></tr>
    </table></body></html>
    """
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "cat" in words
    assert "" not in words


def test_fetch_words_skips_numeric_first_cell():
    html = """
    <html><body><table>
      <tr><td>1</td><td>num</td><td>ipa</td></tr>
      <tr><td>dog</td><td>A dog.</td><td>/dɒɡ/</td></tr>
    </table></body></html>
    """
    with patch("scrape_esl_lounge.requests.get", return_value=_mock_response(html)):
        words = fetch_words("a1", "nouns")
    assert "dog" in words
    assert "1" not in words


def test_write_csv(tmp_path):
    rows = [
        {"word": "apple", "cefr_level": "A1", "pos": "noun"},
        {"word": "run", "cefr_level": "A1", "pos": "verb"},
    ]
    out = tmp_path / "vocab.csv"
    write_csv(rows, out)
    content = out.read_text()
    assert "word,cefr_level,pos" in content
    assert "apple,A1,noun" in content
    assert "run,A1,verb" in content
