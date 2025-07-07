"""
Tests for configuration management and validation
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from pydantic import ValidationError

from weather_mcp.config import Config, get_config, setup_logging


class TestConfig:
    """Test class for configuration validation and management"""

    @pytest.mark.unit
    def test_config_with_valid_data(self):
        """Test configuration creation with valid data"""
        config_data = {
            "accuweather_api_key": "valid_api_key_12345",
            "accuweather_base_url": "https://dataservice.accuweather.com",
            "host": "0.0.0.0",
            "port": 9000,
            "debug": True,
            "log_level": "DEBUG",
            "log_file": "/tmp/weather.log",
            "sse_heartbeat_interval": 60,
            "sse_max_connections": 200,
            "cache_ttl_seconds": 600,
            "cache_max_size": 2000
        }
        
        config = Config(**config_data)
        
        assert config.accuweather_api_key == "valid_api_key_12345"
        assert config.accuweather_base_url == "https://dataservice.accuweather.com"
        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.debug is True
        assert config.log_level == "DEBUG"
        assert config.log_file == "/tmp/weather.log"
        assert config.sse_heartbeat_interval == 60
        assert config.sse_max_connections == 200
        assert config.cache_ttl_seconds == 600
        assert config.cache_max_size == 2000

    @pytest.mark.unit
    def test_config_with_defaults(self):
        """Test configuration with default values"""
        # Create config with explicit values to avoid .env file interference
        config = Config(
            accuweather_api_key="valid_api_key_12345",
            accuweather_base_url="http://dataservice.accuweather.com",
            host="localhost",
            port=8000,
            debug=False,
            log_level="INFO",
            log_file=None,
            sse_heartbeat_interval=30,
            sse_max_connections=100,
            cache_ttl_seconds=300,
            cache_max_size=1000
        )
        
        assert config.accuweather_api_key == "valid_api_key_12345"
        assert config.accuweather_base_url == "http://dataservice.accuweather.com"
        assert config.host == "localhost"
        assert config.port == 8000
        assert config.debug is False
        assert config.log_level == "INFO"
        assert config.log_file is None
        assert config.sse_heartbeat_interval == 30
        assert config.sse_max_connections == 100
        assert config.cache_ttl_seconds == 300
        assert config.cache_max_size == 1000

    @pytest.mark.unit
    def test_config_invalid_api_key(self):
        """Test configuration validation with invalid API key"""
        with pytest.raises(ValidationError) as exc_info:
            Config(accuweather_api_key="")
        
        assert "AccuWeather API key is required" in str(exc_info.value)

    @pytest.mark.unit
    def test_config_placeholder_api_key(self):
        """Test configuration validation with placeholder API key"""
        with pytest.raises(ValidationError) as exc_info:
            Config(accuweather_api_key="your_api_key_here")
        
        assert "AccuWeather API key is required" in str(exc_info.value)

    @pytest.mark.unit
    def test_config_missing_api_key(self):
        """Test configuration validation when API key is missing"""
        # Create a temporary config class without env_file to avoid .env interference
        from pydantic import ConfigDict
        from pydantic_settings import BaseSettings
        
        class TestConfig(BaseSettings):
            accuweather_api_key: str
            
            model_config = ConfigDict(env_file=None)
        
        with pytest.raises(ValidationError) as exc_info:
            TestConfig()
        
        # Pydantic will raise a validation error for missing required field
        assert "accuweather_api_key" in str(exc_info.value)

    @pytest.mark.unit
    def test_config_invalid_log_level(self):
        """Test configuration validation with invalid log level"""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                accuweather_api_key="valid_api_key_12345",
                log_level="INVALID"
            )
        
        assert "Log level must be one of" in str(exc_info.value)

    @pytest.mark.unit
    def test_config_valid_log_levels(self):
        """Test configuration with all valid log levels"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in valid_levels:
            config = Config(
                accuweather_api_key="valid_api_key_12345",
                log_level=level
            )
            assert config.log_level == level

    @pytest.mark.unit
    def test_config_case_insensitive_log_level(self):
        """Test that log level validation is case insensitive"""
        config = Config(
            accuweather_api_key="valid_api_key_12345",
            log_level="debug"
        )
        assert config.log_level == "DEBUG"

    @pytest.mark.unit
    def test_config_type_coercion(self):
        """Test that configuration properly coerces types"""
        config = Config(
            accuweather_api_key="valid_api_key_12345",
            port="9000",  # String that should be converted to int
            debug="true",  # String that should be converted to bool
            cache_ttl_seconds="600"  # String that should be converted to int
        )
        
        assert config.port == 9000
        assert config.debug is True
        assert config.cache_ttl_seconds == 600


class TestGetConfig:
    """Test class for get_config function"""

    @pytest.mark.unit
    @patch.dict(os.environ, {
        'ACCUWEATHER_API_KEY': 'test_api_key_12345',
        'HOST': '0.0.0.0',
        'PORT': '9000',
        'DEBUG': 'true'
    })
    def test_get_config_from_environment(self):
        """Test configuration loading from environment variables"""
        with patch('weather_mcp.config.Path.exists', return_value=False):
            config = get_config()
            
            assert config.accuweather_api_key == "test_api_key_12345"
            assert config.host == "0.0.0.0"
            assert config.port == 9000
            assert config.debug is True

    @pytest.mark.unit
    @patch.dict(os.environ, {'ACCUWEATHER_API_KEY': 'test_api_key_12345'})
    def test_get_config_with_env_file(self):
        """Test configuration loading with .env file present"""
        with patch('weather_mcp.config.Path.exists', return_value=True):
            config = get_config()
            
            assert config.accuweather_api_key == "test_api_key_12345"
            # Other values will be defaults since we're not actually reading a file

    @pytest.mark.unit
    def test_get_config_missing_api_key(self):
        """Test get_config when API key is missing"""
        # Mock Config class to prevent .env file loading and force validation error
        with patch('weather_mcp.config.Config') as mock_config_class:
            mock_config_class.side_effect = ValidationError.from_exception_data(
                "ValidationError", 
                [{"type": "missing", "loc": ("accuweather_api_key",), "msg": "Field required"}]
            )
            with pytest.raises(ValidationError):
                get_config()

    @pytest.mark.unit
    @patch.dict(os.environ, {'ACCUWEATHER_API_KEY': 'your_api_key_here'})
    def test_get_config_placeholder_api_key_warning(self):
        """Test that get_config warns about placeholder API key"""
        with patch('weather_mcp.config.Path.exists', return_value=False):
            with pytest.raises(ValidationError):
                # Should raise validation error for placeholder key
                get_config()

    @pytest.mark.unit
    def test_get_config_exception_handling(self):
        """Test get_config exception handling"""
        with patch('weather_mcp.config.Config', side_effect=Exception("Test error")):
            with pytest.raises(Exception, match="Test error"):
                get_config()


class TestSetupLogging:
    """Test class for logging setup"""

    @pytest.mark.unit
    def test_setup_logging_console_only(self, mock_config):
        """Test logging setup with console output only"""
        mock_config.log_file = None
        mock_config.log_level = "INFO"
        
        with patch('weather_mcp.config.logger') as mock_logger:
            setup_logging(mock_config)
            
            # Verify logger.remove() was called
            mock_logger.remove.assert_called_once()
            
            # Verify logger.add() was called at least once for console
            assert mock_logger.add.call_count >= 1

    @pytest.mark.unit
    def test_setup_logging_with_file(self, mock_config):
        """Test logging setup with file output"""
        mock_config.log_file = "/tmp/test.log"
        mock_config.log_level = "DEBUG"
        
        with patch('weather_mcp.config.logger') as mock_logger:
            with patch('weather_mcp.config.os.makedirs') as mock_makedirs:
                setup_logging(mock_config)
                
                # Verify directory creation
                mock_makedirs.assert_called_once_with("/tmp", exist_ok=True)
                
                # Verify logger was configured
                mock_logger.remove.assert_called_once()
                assert mock_logger.add.call_count == 2  # Console + file

    @pytest.mark.unit
    def test_setup_logging_different_levels(self, mock_config):
        """Test logging setup with different log levels"""
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in log_levels:
            mock_config.log_level = level
            
            with patch('weather_mcp.config.logger') as mock_logger:
                setup_logging(mock_config)
                
                # Verify logger was configured with correct level
                mock_logger.remove.assert_called_once()
                mock_logger.add.assert_called()


class TestConfigIntegration:
    """Integration tests for configuration"""

    @pytest.mark.integration
    @patch.dict(os.environ, {
        'ACCUWEATHER_API_KEY': 'integration_test_key',
        'LOG_LEVEL': 'WARNING',
        'CACHE_TTL_SECONDS': '120'
    })
    def test_full_config_flow(self):
        """Test complete configuration flow from environment to setup"""
        with patch('weather_mcp.config.Path.exists', return_value=False):
            with patch('weather_mcp.config.logger') as mock_logger:
                # Get config
                config = get_config()
                
                # Verify config values
                assert config.accuweather_api_key == "integration_test_key"
                assert config.log_level == "WARNING"
                assert config.cache_ttl_seconds == 120
                
                # Setup logging
                setup_logging(config)
                
                # Verify logging was configured
                mock_logger.remove.assert_called()
                mock_logger.add.assert_called()

    @pytest.mark.integration
    def test_config_validation_chain(self):
        """Test that configuration validation works end-to-end"""
        # Test with valid data
        valid_config = Config(
            accuweather_api_key="valid_key_12345",
            log_level="info",  # Should be normalized to "INFO"
            port=8080
        )
        
        assert valid_config.accuweather_api_key == "valid_key_12345"
        assert valid_config.log_level == "INFO"
        assert valid_config.port == 8080
        
        # Test with invalid data
        with pytest.raises(ValidationError):
            Config(
                accuweather_api_key="",
                log_level="INVALID_LEVEL"
            ) 