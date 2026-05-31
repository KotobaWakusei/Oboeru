"""Unit tests for progress_manager.py module."""
import pytest
from datetime import datetime, timedelta

from modules.progress_manager import ProgressManager, StudySession, WordProgress


class TestProgressManager:
    """Test ProgressManager class."""

    def test_session_lifecycle(self, progress_manager: ProgressManager) -> None:
        """Test starting and ending a study session."""
        progress_manager.start_session()
        assert progress_manager.session_start_time is not None

        progress_manager.record_answer("apple", True)
        progress_manager.record_answer("banana", False)
        progress_manager.record_answer("cat", True)

        progress_manager.end_session(words_studied=3, words_reviewed=1)
        assert len(progress_manager.study_sessions) == 1

        session = progress_manager.study_sessions[0]
        assert session.words_studied == 3
        assert session.words_reviewed == 1
        assert session.accuracy_rate > 0

    def test_record_answer_correct(self, progress_manager: ProgressManager) -> None:
        """Test recording correct answers."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        assert "apple" in progress_manager.word_progress
        wp = progress_manager.word_progress["apple"]
        assert wp.correct_count == 1
        assert wp.wrong_count == 0
        assert wp.total_study_count == 1

    def test_record_answer_wrong(self, progress_manager: ProgressManager) -> None:
        """Test recording wrong answers."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", False)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        wp = progress_manager.word_progress["apple"]
        assert wp.correct_count == 0
        assert wp.wrong_count == 1
        assert wp.mastery_level == 0

    def test_mastery_level_progression(self, progress_manager: ProgressManager) -> None:
        """Test that correct answers increase mastery level."""
        progress_manager.start_session()
        for i in range(5):
            progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        wp = progress_manager.word_progress["apple"]
        assert wp.mastery_level == 5
        assert wp.correct_count == 5

    def test_mastery_level_decrease(self, progress_manager: ProgressManager) -> None:
        """Test that wrong answers decrease mastery level."""
        progress_manager.start_session()
        for i in range(3):
            progress_manager.record_answer("apple", True)
        progress_manager.record_answer("apple", False)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        wp = progress_manager.word_progress["apple"]
        assert wp.mastery_level == 2

    def test_accuracy_rate(self, progress_manager: ProgressManager) -> None:
        """Test accuracy rate calculation."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.record_answer("apple", True)
        progress_manager.record_answer("apple", False)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        wp = progress_manager.word_progress["apple"]
        assert wp.accuracy_rate == 2.0 / 3.0

    def test_get_statistics_empty(self, progress_manager: ProgressManager) -> None:
        """Test statistics when no sessions exist."""
        stats = progress_manager.get_statistics()
        assert stats["total_sessions"] == 0
        assert stats["total_words_studied"] == 0
        assert stats["average_accuracy"] == 0.0

    def test_get_statistics_after_session(self, progress_manager: ProgressManager) -> None:
        """Test statistics after recording a session."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.record_answer("banana", True)
        progress_manager.end_session(words_studied=2, words_reviewed=0)

        stats = progress_manager.get_statistics()
        assert stats["total_sessions"] == 1
        assert stats["total_words_studied"] == 2
        assert stats["average_accuracy"] > 0

    def test_get_due_words(self, progress_manager: ProgressManager) -> None:
        """Test getting due words for review."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        all_words = ["apple", "banana", "cat"]
        due = progress_manager.get_due_words(all_words)
        assert "banana" in due
        assert "cat" in due

    def test_clear_all_progress(self, progress_manager: ProgressManager) -> None:
        """Test clearing all progress."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        progress_manager.clear_all_progress()
        assert len(progress_manager.study_sessions) == 0
        assert len(progress_manager.word_progress) == 0

    def test_mastered_count_property(self, progress_manager: ProgressManager) -> None:
        """Test the mastered_count property."""
        progress_manager.start_session()
        for i in range(5):
            progress_manager.record_answer("apple", True)
        progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        wp = progress_manager.word_progress["apple"]
        wp.review_count = 2
        wp.check_and_update_mastery()

        assert progress_manager.mastered_count >= 0

    def test_reviewing_words_property(self, progress_manager: ProgressManager) -> None:
        """Test the reviewing_words property."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        reviewing = progress_manager.reviewing_words
        assert isinstance(reviewing, list)

    def test_word_statistics(self, progress_manager: ProgressManager) -> None:
        """Test getting statistics for a specific word."""
        progress_manager.start_session()
        progress_manager.record_answer("apple", True)
        progress_manager.end_session(words_studied=1, words_reviewed=0)

        stats = progress_manager.get_word_statistics("apple")
        assert stats is not None
        assert stats["word"] == "apple"
        assert stats["total_study_count"] >= 1

        no_stats = progress_manager.get_word_statistics("nonexistent")
        assert no_stats is None
