from app.services.core.quote import get_quote

def test_get_quote():
    quote = get_quote()
    # The quote should be a non-empty string and contain a dash (author)
    assert isinstance(quote, str)
    assert len(quote) > 0
    assert "–" in quote or "-" in quote 