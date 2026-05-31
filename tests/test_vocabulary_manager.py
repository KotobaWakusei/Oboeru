"""Unit tests for vocabulary_manager.py module."""
import pytest
import os
from typing import List

from modules.vocabulary_manager import VocabularyManager
from modules.base_word import VocabularyWord


class TestVocabularyManager:
    """Test VocabularyManager class."""

    def test_load_from_strings(self, vocabulary_manager: VocabularyManager) -> None:
        """Test loading vocabulary from strings."""
        lines = [
            "apple\tn.\t苹果",
            "banana\tn.\t香蕉",
            "cat\tn.\t猫",
        ]
        count = vocabulary_manager.load_from_strings(lines)
        assert count == 3
        assert len(vocabulary_manager) == 3

    def test_load_from_file(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test loading vocabulary from file."""
        success, result = vocabulary_manager.load_from_file(sample_vocab_file)
        assert success is True
        assert isinstance(result, int)
        assert result > 0

    def test_load_from_nonexistent_file(
        self, vocabulary_manager: VocabularyManager
    ) -> None:
        """Test loading from nonexistent file."""
        success, result = vocabulary_manager.load_from_file("/nonexistent/path.txt")
        assert success is False
        assert "不存在" in str(result) or "doesn't exist" in str(result)

    def test_get_word_by_index(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test getting a word by index."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        word = vocabulary_manager.get_word_by_index(0)
        assert word is not None
        assert word.word == "apple"

        word2 = vocabulary_manager.get_word_by_index(99)
        assert word2 is None

    def test_get_word_by_text(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test getting a word by text lookup."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        word = vocabulary_manager.get_word_by_text("apple")
        assert word is not None
        assert word.meaning == "苹果"

        none_word = vocabulary_manager.get_word_by_text("nonexistent")
        assert none_word is None

    def test_search_words(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test searching words by query."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        results = vocabulary_manager.search_words("apple")
        assert len(results) >= 1
        assert results[0].word == "apple"

        results2 = vocabulary_manager.search_words("香蕉")
        assert len(results2) >= 1

        results3 = vocabulary_manager.search_words("zzz_not_found")
        assert len(results3) == 0

    def test_get_words(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test getting words with count and shuffle."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        all_words = vocabulary_manager.get_words()
        assert len(all_words) == 5

        limited = vocabulary_manager.get_words(count=2)
        assert len(limited) == 2

        shuffled = vocabulary_manager.get_words(shuffle=True)
        assert len(shuffled) == 5

    def test_generate_options(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test generating multiple-choice options."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        word = vocabulary_manager.get_word_by_index(0)
        assert word is not None

        options = vocabulary_manager.generate_options(word, count=3)
        assert len(options) == 4
        assert word.meaning in options

    def test_len_and_bool(
        self, vocabulary_manager: VocabularyManager
    ) -> None:
        """Test __len__ and __bool__."""
        assert len(vocabulary_manager) == 0
        assert bool(vocabulary_manager) is False

        vocabulary_manager.load_from_strings(["test\tn.\t测试"])
        assert len(vocabulary_manager) == 1
        assert bool(vocabulary_manager) is True

    def test_iteration(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test iterating over vocabulary."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        words = list(vocabulary_manager)
        assert len(words) == 5
        assert all(isinstance(w, VocabularyWord) for w in words)

    def test_get_statistics(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test getting vocabulary statistics."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        stats = vocabulary_manager.get_statistics()
        assert stats["total_words"] == 5
        assert "n." in stats["unique_pos"]
        assert "adj." in stats["unique_pos"]

    def test_clear_cache(
        self, vocabulary_manager: VocabularyManager, sample_vocab_file: str
    ) -> None:
        """Test clearing the LRU cache."""
        vocabulary_manager.load_from_file(sample_vocab_file)
        vocabulary_manager.clear_cache()
        stats = vocabulary_manager.cache_stats
        assert "hits" in stats
        assert "misses" in stats
