import nltk
from nltk.util import ngrams
from collections import Counter
import os
import pickle
import re
import random

USER_DATA_FILE = "user_data.txt"
TRIGRAM_MODEL_FILE = "trigram_model.pkl"
BIGRAM_MODEL_FILE = "bigram_model.pkl"
ARABIC_CORPUS_FILE = "arabic_corpus.txt"


def load_arabic_text():
    if not os.path.exists(ARABIC_CORPUS_FILE):
        return ""

    with open(ARABIC_CORPUS_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def arabic_tokenizer(text):
    return re.findall(r'[\u0600-\u06FF\u0750-\u077F]+', text)


def load_models():
    if os.path.exists(TRIGRAM_MODEL_FILE) and os.path.exists(BIGRAM_MODEL_FILE):
        with open(TRIGRAM_MODEL_FILE, "rb") as f:
            trigram_model = pickle.load(f)
        with open(BIGRAM_MODEL_FILE, "rb") as f:
            bigram_model = pickle.load(f)
    else:
        nltk.download('gutenberg')
        nltk.download('punkt')

        from nltk.corpus import gutenberg
        from nltk.tokenize import word_tokenize

        english_text = gutenberg.raw('austen-emma.txt').lower()
        english_tokens = word_tokenize(english_text)

        arabic_text = load_arabic_text()
        arabic_tokens = arabic_tokenizer(arabic_text)

        combined_tokens = english_tokens + arabic_tokens

        trigrams = list(ngrams(combined_tokens, 3))
        bigrams = list(ngrams(combined_tokens, 2))

        trigram_model = Counter(trigrams)
        bigram_model = Counter(bigrams)

        with open(TRIGRAM_MODEL_FILE, "wb") as f:
            pickle.dump(trigram_model, f)
        with open(BIGRAM_MODEL_FILE, "wb") as f:
            pickle.dump(bigram_model, f)

    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 3:
                    trigram_model[tuple(parts)] += 1

    return trigram_model, bigram_model


def predict_next_words(word1, word2, trigram_model, bigram_model, top_n=5):
    candidates = {k[2]: v for k, v in trigram_model.items() if k[0] == word1 and k[1] == word2}

    if not candidates:
        candidates = {k[1]: v for k, v in bigram_model.items() if k[0] == word2}

    sorted_candidates = sorted(candidates.items(), key=lambda item: item[1], reverse=True)
    return [word for word, count in sorted_candidates[:top_n]]


def generate_sentences(start_words, trigram_model, bigram_model, max_words=8, num_sentences=3):
    sentences = set()
    max_attempts = 10
    attempts = 0

    while len(sentences) < num_sentences and attempts < max_attempts:
        attempts += 1
        words = start_words.copy()

        for _ in range(max_words):
            if len(words) < 2:
                break

            w1, w2 = words[-2], words[-1]
            candidates = predict_next_words(w1, w2, trigram_model, bigram_model, top_n=3)
            if not candidates:
                break

            next_word = random.choice(candidates)
            words.append(next_word)

            if next_word in ['.', '؟', '!', '…']:
                break

        sentence = ' '.join(words).strip()
        if sentence:
            sentences.add(sentence)

    return list(sentences)[:num_sentences]