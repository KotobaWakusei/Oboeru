"""Pytest configuration and shared fixtures."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import pytest
import tempfile
import json
from typing import Generator, Dict, Any

from modules.config_manager import ConfigManager
from modules.vocabulary_manager import VocabularyManager
from modules.favorites_manager import FavoritesManager
from modules.progress_manager import ProgressManager


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def config_manager(temp_dir: str) -> ConfigManager:
    """Create a ConfigManager instance for testing."""
    config_file = f"{temp_dir}/test_config.json"
    manager = ConfigManager(config_file=config_file)
    yield manager


@pytest.fixture
def vocabulary_manager() -> VocabularyManager:
    """Create a VocabularyManager instance for testing."""
    return VocabularyManager()


@pytest.fixture
def sample_vocab_file(temp_dir: str) -> str:
    """Create a sample vocabulary file for testing."""
    vocab_file = f"{temp_dir}/test_vocab.txt"
    content = """# Sample vocabulary for testing
apple	n.	苹果	application,apply
banana	n.	香蕉	band,ban
cat	n.	猫	cart,cut,cap
dog	n.	狗	dig,do,dark
good	adj.	好的	god,food,wood
"""
    with open(vocab_file, 'w', encoding='utf-8') as f:
        f.write(content)
    return vocab_file


@pytest.fixture
def favorites_manager(temp_dir: str) -> FavoritesManager:
    """Create a FavoritesManager instance for testing."""
    favorites_file = f"{temp_dir}/test_favorites.txt"
    manager = FavoritesManager(favorites_file=favorites_file)
    yield manager


@pytest.fixture
def progress_manager(temp_dir: str) -> ProgressManager:
    """Create a ProgressManager instance for testing."""
    progress_file = f"{temp_dir}/test_progress.json"
    manager = ProgressManager(progress_file=progress_file)
    yield manager
