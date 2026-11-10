import re


def split_sentences(text: str) -> list[str]:
    if not text.strip():
        return []
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def extract(text: str) -> tuple[list[str], list[str]]:
    sentences = split_sentences(text)
    if not sentences:
        return [], []
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            return sentences, []
        entities: list[str] = []
        for sent in sentences:
            doc = nlp(sent)
            entities.extend([ent.text for ent in doc.ents])
        return sentences, list(set(entities))
    except ImportError:
        return sentences, []
