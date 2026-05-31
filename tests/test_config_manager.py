"""Unit tests for config_manager.py module."""
import pytest
import json
import os
from pathlib import Path

from modules.config_manager import ConfigManager
from modules.utils.constants import Constants


class TestConfigManager:
    """Test ConfigManager class."""

    def test_load_config_default(self, config_manager: ConfigManager) -> None:
        """Test loading default configuration."""
        config = config_manager.get_default_config()
        assert isinstance(config, dict)
        assert "daily_words" in config
        assert config["daily_words"] == Constants.DAILY_WORDS_DEFAULT

    def test_get_and_set_config(self, config_manager: ConfigManager) -> None:
        """Test getting and setting configuration values."""
        # Set a value
        config_manager.set("test_key", "test_value")
        
        # Get the value
        value = config_manager.get("test_key")
        assert value == "test_value"

    def test_get_with_default(self, config_manager: ConfigManager) -> None:
        """Test get method with default value."""
        value = config_manager.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_get_bool(self, config_manager: ConfigManager) -> None:
        """Test get_bool method."""
        config_manager.set("bool_key", True)
        assert config_manager.get_bool("bool_key") is True
        
        config_manager.set("bool_key", False)
        assert config_manager.get_bool("bool_key") is False

    def test_get_int(self, config_manager: ConfigManager) -> None:
        """Test get_int method."""
        config_manager.set("int_key", 42)
        assert config_manager.get_int("int_key") == 42
        
        config_manager.set("int_key", "100")
        assert config_manager.get_int("int_key") == 100

    def test_set_multiple_values(self, config_manager: ConfigManager) -> None:
        """Test setting multiple configuration values."""
        values = {
            "key1": "value1",
            "key2": "value2",
            "key3": 123,
        }
        for key, value in values.items():
            config_manager.set(key, value)
        
        for key, expected_value in values.items():
            assert config_manager.get(key) == expected_value

    def test_get_float(self, config_manager: ConfigManager) -> None:
        """Test get_float method."""
        config_manager.set("float_key", 3.14)
        result = config_manager.get_float("float_key")
        assert abs(result - 3.14) < 0.01

    def test_save_and_load_config(self, temp_dir: str) -> None:
        """Test saving and loading configuration from file."""
        config_file = f"{temp_dir}/config.json"
        manager1 = ConfigManager(config_file=config_file)
        
        # Set and save
        manager1.set("test_key", "test_value")
        manager1.set("number_key", 42)
        manager1.save_config()
        
        # Load in new instance
        manager2 = ConfigManager(config_file=config_file)
        assert manager2.get("test_key") == "test_value"
        assert manager2.get("number_key") == 42

    def test_config_persistence(self, config_manager: ConfigManager) -> None:
        """Test that configuration changes are persistent."""
        config_manager.set("persistent_key", "persistent_value")
        config_manager.save_config()
        
        value = config_manager.get("persistent_key")
        assert value == "persistent_value"

    @pytest.mark.parametrize("key,value,expected", [
        ("daily_words", 25, 25),
        ("font_size", 16, 16),
        ("theme", "dark", "dark"),
    ])
    def test_various_config_values(
        self, config_manager: ConfigManager, key: str, value: str, expected: str
    ) -> None:
        """Test various configuration values."""
        config_manager.set(key, value)
        assert config_manager.get(key) == expected
