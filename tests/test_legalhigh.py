"""Tests for LegalHigh."""
import pytest
from legalhigh import LegalHigh


def test_legalhigh_init():
    app = LegalHigh()
    assert app.documents == []


def test_add_document():
    app = LegalHigh()
    app.add_document("doc1.pdf")
    assert app.get_documents() == ["doc1.pdf"]


def test_add_multiple_documents():
    app = LegalHigh()
    app.add_document("doc1.pdf")
    app.add_document("doc2.pdf")
    assert len(app.get_documents()) == 2


def test_get_documents_returns_copy():
    app = LegalHigh()
    app.add_document("doc.pdf")
    docs = app.get_documents()
    docs.append("extra.pdf")
    assert len(app.get_documents()) == 1


def test_method_chaining():
    app = LegalHigh()
    result = app.add_document("doc1.pdf").add_document("doc2.pdf")
    assert result is app
    assert len(app.get_documents()) == 2


def test_run(capsys):
    app = LegalHigh()
    app.run()
    captured = capsys.readouterr()
    assert "LegalHigh" in captured.out
