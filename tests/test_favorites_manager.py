"""Unit tests for favorites_manager.py module."""
import pytest

from modules.favorites_manager import FavoritesManager, FavoriteWord


class TestFavoritesManager:
    """Test FavoritesManager class."""

    def test_add_word(self, favorites_manager: FavoritesManager) -> None:
        """Test adding a favorite word."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        result = favorites_manager.add_word(word)
        assert result is True

    def test_is_favorite(self, favorites_manager: FavoritesManager) -> None:
        """Test checking if word is favorite."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        favorites_manager.add_word(word)
        assert favorites_manager.is_favorite("apple") is True
        assert favorites_manager.is_favorite("banana") is False

    def test_remove_word(self, favorites_manager: FavoritesManager) -> None:
        """Test removing a favorite."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        favorites_manager.add_word(word)
        result = favorites_manager.remove_word("apple")
        assert result is True
        assert favorites_manager.is_favorite("apple") is False

    def test_get_all_words(self, favorites_manager: FavoritesManager) -> None:
        """Test getting all favorites."""
        word1 = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        word2 = FavoriteWord(word="banana", pos="n.", meaning="香蕉")
        favorites_manager.add_word(word1)
        favorites_manager.add_word(word2)
        
        words = favorites_manager.get_all_words()
        assert len(words) >= 2

    def test_clear_all(self, favorites_manager: FavoritesManager) -> None:
        """Test clearing all favorites."""
        word1 = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        word2 = FavoriteWord(word="banana", pos="n.", meaning="香蕉")
        favorites_manager.add_word(word1)
        favorites_manager.add_word(word2)
        
        favorites_manager.clear_all()
        assert len(favorites_manager.get_all_words()) == 0

    def test_get_word(self, favorites_manager: FavoritesManager) -> None:
        """Test getting a specific word."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        favorites_manager.add_word(word)
        
        retrieved_word = favorites_manager.get_word("apple")
        assert retrieved_word is not None
        assert retrieved_word.word == "apple"

    def test_increment_learn_count(self, favorites_manager: FavoritesManager) -> None:
        """Test incrementing learn count."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        favorites_manager.add_word(word)
        
        result = favorites_manager.increment_learn_count("apple")
        assert result is True

    def test_set_mastered(self, favorites_manager: FavoritesManager) -> None:
        """Test setting mastered status."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        favorites_manager.add_word(word)
        
        result = favorites_manager.set_mastered("apple", True)
        assert result is True

    def test_add_duplicate_word(self, favorites_manager: FavoritesManager) -> None:
        """Test adding duplicate word."""
        word = FavoriteWord(word="apple", pos="n.", meaning="苹果")
        favorites_manager.add_word(word)
        result = favorites_manager.add_word(word)
        # Should handle duplicates gracefully
        assert isinstance(result, bool)

    def test_remove_nonexistent_word(self, favorites_manager: FavoritesManager) -> None:
        """Test removing nonexistent word."""
        result = favorites_manager.remove_word("nonexistent")
        # Should handle gracefully
        assert isinstance(result, bool)

    @pytest.mark.parametrize("word,pos,meaning", [
        ("apple", "n.", "苹果"),
        ("banana", "n.", "香蕉"),
        ("run", "v.", "跑步"),
    ])
    def test_multiple_words(
        self, favorites_manager: FavoritesManager, word: str, pos: str, meaning: str
    ) -> None:
        """Test adding multiple different words."""
        fav_word = FavoriteWord(word=word, pos=pos, meaning=meaning)
        result = favorites_manager.add_word(fav_word)
        assert result is True
        assert favorites_manager.is_favorite(word) is True

