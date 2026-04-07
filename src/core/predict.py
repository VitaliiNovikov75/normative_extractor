# predict.py
import re
import joblib
import pandas as pd
import numpy as np
from natasha import (
    Segmenter, MorphVocab, NewsEmbedding,
    NewsMorphTagger, Doc
)
import os
import sys
sys.path.append(os.path.abspath('..'))

class TextClassifier:
    def __init__(self, path_model):
        self.model = joblib.load(path_model)
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.MODAL_LEMMAS = {
            'должный', 'следовать', 'необходимо', 'допускаться', 'запрещаться',
            'менее', 'более', 'предел', 'погрешность'
        }
        #self.last_lemmas = ''

    def _extract_morph_features(self, texts: list[str]) -> pd.DataFrame:
        """Метод для морфологии"""
        rows = []
        for text in texts:
            if not text or not isinstance(text, str):
                rows.append({'lemma_text': '', 'modal': 0, 'verb_count': 0, 'n_nouns': 0})
                continue

            t_s = text.strip()
            doc = Doc(t_s)
            doc.segment(self.segmenter)
            doc.tag_morph(self.morph_tagger)
            lemmas = []
            modal, inf_count, verb_count, n_nouns, n_gen_nouns = 0, 0, 0, 0, 0

            for t in doc.tokens:
                t.lemmatize(self.morph_vocab)
                lemmas.append(t.lemma)
                if t.lemma in self.MODAL_LEMMAS: modal = 1
                if t.pos in ('VERB', 'AUX'):
                    verb_count += 1
                    if t.feats.get('VerbForm') == 'Inf': inf_count += 1
                elif t.pos == 'NOUN':
                    n_nouns += 1
                    if t.feats.get('Case') == 'Gen': n_gen_nouns += 1

            rows.append({
                'lemma_text': ' '.join(lemmas),
                'modal': modal,
                'inf_count': inf_count,
                'verb_count': verb_count,
                'genitive_ratio': round(n_gen_nouns / n_nouns, 3) if n_nouns > 0 else 0.0,
                'cap_start': int(t_s[0].isupper()) if t_s else 0,
                'ends_dot': int(t_s.endswith('.')),
                'ends_semi': int(t_s.endswith(';')),
                'list_marker': int(bool(re.match(r'^(\d+\.?|[а-яё]\)|\d+\))', t_s))),
                'text_len': len(t_s),
                'digit_density': round(sum(c.isdigit() for c in t_s) / len(t_s), 2) if len(t_s) > 0 else 0.0,
                'all_caps': int(t_s.isupper() and len(t_s) > 5)
            })
        return pd.DataFrame(rows)

    def preprocess(self, texts: list[str]) -> pd.Series:
        """Сборка признаков в текстовую строку для классификатора"""
        df = self._extract_morph_features(texts)
        #self.last_lemmas = ' '.join(df['lemma_text'].astype(str))
        res = df['lemma_text'].copy()

        res += np.where(df['modal'] == 1, ' MODAL', '')
        res += np.where(df['verb_count'] == 0, ' NO_VERB', '')
        res += np.where(df['cap_start'] == 1, ' CAP_START', '')
        res += np.where(df['ends_dot'] == 1, ' ENDS_DOT', '')
        res += np.where(df['all_caps'] == 1, ' ALL_CAPS', '')
        res += np.where(df['text_len'] < 35, ' TOKEN_SHORT', '')

        list_semi = (df['list_marker'] == 1) | (df['ends_semi'] == 1)
        res += np.where(list_semi, ' LIST_MARKER_SEMI', '')

        return res.str.strip()

    def predict(self, texts: list[str]):
        """Точка входа"""
        processed_text = self.preprocess(texts)
        return self.model.predict(processed_text)
