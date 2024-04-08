from search.tokenizer import tokenize


def test_tokenize():
    text = (
        "In publishing and graphic design, Lorem ipsum is a placeholder text "
        "commonly used to demonstrate the visual form of a document or a "
        "typeface without relying on meaningful content."
    )
    expected = [
        "publishing",
        "graphic",
        "design",
        "lorem",
        "ipsum",
        "placeholder",
        "text",
        "commonly",
        "used",
        "demonstrate",
        "visual",
        "form",
        "document",
        "typeface",
        "without",
        "relying",
        "meaningful",
        "content",
    ]
    assert list(tokenize(text)) == expected
