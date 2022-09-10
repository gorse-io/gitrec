from typing import List, Optional

import inflect
import nltk
from gorse import Gorse


class LabelGenerator:
    def __init__(self, gorse_client: Gorse, min_freq: Optional[int] = 5):
        # Download punkt
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        # Create singular noun converter
        self.inflect = inflect.engine()
        # Load existed topics
        topic_count = dict()
        cursor = ""
        while True:
            items, cursor = gorse_client.get_items(1000, cursor)
            for item in items:
                if item["Labels"] is not None:
                    for topic in item["Labels"]:
                        if topic not in topic_count:
                            topic_count[topic] = 1
                        else:
                            topic_count[topic] += 1
            if cursor == "":
                break
        self.topics = []
        for topic, count in topic_count.items():
            if count >= min_freq:
                self.topics.append(topic)

    def extract(self, text: Optional[str]) -> List[str]:
        if text is None:
            return []
        # Tokenize description
        tokens = nltk.word_tokenize(text)
        tokens = [v.lower() for v in tokens]
        # Convert plural to singular noun
        append_tokens = []
        for token in tokens:
            singular = self.inflect.singular_noun(token)
            if singular:
                append_tokens.append(singular)
        tokens.extend(append_tokens)
        sentence = "-".join(tokens)
        labels = []
        for label in self.topics:
            if "-" not in label:
                if label in tokens:
                    labels.append(label)
            else:
                if label in sentence:
                    labels.append(label)
        return labels

    def optimize(self, item: dict) -> Optional[dict]:
        # description is required
        if item["Comment"] is None or len(item["Comment"]) == 0:
            return None
        # extract topics
        labels = self.extract(item["Comment"])
        if len(labels) == 0:
            return None
        if item["Labels"] is not None and len(item["Labels"]) > 0:
            labels.extend(item["Labels"])
        # update labels
        labels = list(set(labels))
        if item["Labels"] is not None and len(labels) <= len(item["Labels"]):
            return None
        item["Labels"] = labels
        return item
