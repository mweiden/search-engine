from typing import Iterator

# import re
#
# WORD_REGEXP = re.compile(r'\b\w+\b')
#
# def tokenize(text: str) -> Iterator[str]:
#    for match in WORD_REGEXP.finditer(text):
#        yield match.group().lower()

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# NLTK 3.9 split tokenizer tables into a separate
# resource named "punkt_tab". Download both for
# compatibility across environments/CI.
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)

LEMMATIZER = WordNetLemmatizer()


def tokenize(text: str) -> Iterator[str]:
    tokens = [word.lower() for word in word_tokenize(text)]
    return [
        LEMMATIZER.lemmatize(word)
        for word in tokens
        if word not in stopwords.words("english") and word not in string.punctuation
    ]
