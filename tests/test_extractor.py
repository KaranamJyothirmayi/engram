from engram.extractor import extract, split_sentences


def test_split_sentences_basic():
    result = split_sentences("Hello world. This is a test.")
    assert len(result) == 2
    assert result[0] == "Hello world."
    assert result[1] == "This is a test."


def test_split_sentences_single():
    assert split_sentences("Just one sentence") == ["Just one sentence"]


def test_split_empty_string():
    assert split_sentences("") == []


def test_extract_returns_sentences_and_entities():
    sentences, entities = extract("Marie Curie was born in Warsaw.")
    assert "Marie Curie was born in Warsaw." in sentences
    assert isinstance(entities, list)


def test_extract_multiple_sentences():
    sentences, _ = extract("The cat sat. The dog ran.")
    assert len(sentences) == 2


def test_extract_empty_string():
    sentences, entities = extract("")
    assert sentences == [] and entities == []
