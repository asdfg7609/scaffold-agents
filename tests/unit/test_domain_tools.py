"""
tests/unit/test_domain_tools.py

Tests pure functions in domain/tools/ without any LLM or framework.
Real value of DIP: no mocks needed — pure functions can just be called directly.
"""
import pytest
from domain.tools.green.search import search_news, read_url
from domain.tools.yellow.write_file import write_file, read_file, list_files


class TestSearchTools:

    def test_search_returns_results(self):
        r = search_news(query="AI agents", max_results=3)
        assert r["query"] == "AI agents"
        assert len(r["results"]) <= 3

    def test_schema_rejects_invalid_max(self):
        from pydantic import ValidationError
        from domain.tools.green.search import SearchNewsParams
        with pytest.raises(ValidationError):
            SearchNewsParams(query="test", max_results=100)

    def test_invalid_url_returns_error(self):
        r = read_url("ftp://example.com")
        assert "error" in r
        assert "http://" in r["error"]

    def test_valid_url_returns_content(self):
        r = read_url("https://example.com/news")
        assert r["url"] == "https://example.com/news"


class TestFileTools:

    def test_write_and_read(self):
        write_file("unit_test.txt", "test content")
        r = read_file("unit_test.txt")
        assert r["success"] is True
        assert r["content"] == "test content"

    def test_idempotency(self):
        key = "idempotency-test-key-unit"
        write_file("idem.txt", "content1", idempotency_key=key)
        r2 = write_file("idem.txt", "content2", idempotency_key=key)
        assert r2.get("idempotent") is True

    def test_path_traversal_blocked(self):
        r = write_file("../../../etc/passwd", "malicious")
        assert r["success"] is False
        assert "allowed directory" in r["error"]

    def test_nonexistent_file_instructional_error(self):
        r = read_file("no_such_file_xyz.txt")
        assert r["success"] is False
        assert "list_files()" in r["error"]

    def test_list_files(self):
        r = list_files()
        assert "files" in r
        assert "count" in r
