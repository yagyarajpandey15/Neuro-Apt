"""
Unit tests for logging configuration module.

These tests verify that the logging infrastructure works correctly
and can handle various error scenarios.
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import logging

# Import the module to test
from neuroapt.app.utils.logging_config import (
    setup_logging_directory,
    get_ai_logger,
    log_ai_error,
    log_pattern_analysis,
    log_api_call,
    LOG_DIR,
    AI_ERROR_LOG,
    AI_DEBUG_LOG,
    PATTERN_ANALYSIS_LOG
)


class TestLoggingConfiguration(unittest.TestCase):
    """Test suite for logging configuration."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for logs
        self.test_log_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Clear logger handlers and close them to release file locks
        for logger_name in ['test_logger', 'neuroapt.api_calls']:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)
        
        # Remove temporary log directory
        if os.path.exists(self.test_log_dir):
            try:
                shutil.rmtree(self.test_log_dir)
            except PermissionError:
                # On Windows, files might still be locked
                pass
    
    def test_setup_logging_directory_creates_directory(self):
        """Test that setup_logging_directory creates the logs directory."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            # Remove directory if it exists
            if os.path.exists(self.test_log_dir):
                shutil.rmtree(self.test_log_dir)
            
            # Call setup function
            log_path = setup_logging_directory()
            
            # Verify directory was created
            self.assertTrue(os.path.exists(log_path))
            self.assertTrue(os.path.isdir(log_path))
    
    def test_setup_logging_directory_handles_existing_directory(self):
        """Test that setup_logging_directory works when directory already exists."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            # Directory already exists from setUp
            log_path = setup_logging_directory()
            
            # Should not raise error
            self.assertTrue(os.path.exists(log_path))
    
    def test_get_ai_logger_returns_configured_logger(self):
        """Test that get_ai_logger returns a properly configured logger."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            logger = get_ai_logger('test_logger')
            
            # Verify logger is configured
            self.assertIsInstance(logger, logging.Logger)
            self.assertEqual(logger.name, 'test_logger')
            self.assertEqual(logger.level, logging.INFO)
            
            # Verify handlers are attached
            self.assertGreater(len(logger.handlers), 0)
    
    def test_get_ai_logger_avoids_duplicate_handlers(self):
        """Test that get_ai_logger doesn't add duplicate handlers."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            logger1 = get_ai_logger('test_logger')
            handler_count_1 = len(logger1.handlers)
            
            # Get same logger again
            logger2 = get_ai_logger('test_logger')
            handler_count_2 = len(logger2.handlers)
            
            # Should have same number of handlers
            self.assertEqual(handler_count_1, handler_count_2)
            self.assertIs(logger1, logger2)
    
    def test_log_ai_error_writes_to_file(self):
        """Test that log_ai_error writes error information to file."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            log_ai_error(
                component="Test Component",
                operation="test_operation",
                error_type="Test Error",
                error_message="This is a test error",
                user_id=123,
                test_result_id=456,
                details="Additional details",
                fallback_triggered=True
            )
            
            # Verify file was created
            error_log_path = os.path.join(self.test_log_dir, AI_ERROR_LOG)
            self.assertTrue(os.path.exists(error_log_path))
            
            # Verify content
            with open(error_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("Test Component", content)
                self.assertIn("test_operation", content)
                self.assertIn("Test Error", content)
                self.assertIn("This is a test error", content)
                self.assertIn("User ID: 123", content)
                self.assertIn("Test Result ID: 456", content)
                self.assertIn("Additional details", content)
                self.assertIn("Fallback Triggered: Yes", content)
    
    def test_log_ai_error_handles_optional_fields(self):
        """Test that log_ai_error works with minimal required fields."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            log_ai_error(
                component="Test Component",
                operation="test_operation",
                error_type="Test Error",
                error_message="Minimal error"
            )
            
            # Verify file was created
            error_log_path = os.path.join(self.test_log_dir, AI_ERROR_LOG)
            self.assertTrue(os.path.exists(error_log_path))
            
            # Verify content
            with open(error_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("Test Component", content)
                self.assertIn("Minimal error", content)
                self.assertIn("Fallback Triggered: No", content)
    
    def test_log_pattern_analysis_writes_to_file(self):
        """Test that log_pattern_analysis writes analysis data to file."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            log_pattern_analysis(
                test_result_id=789,
                pattern_classification="decisive",
                consistency_score=85.5,
                contradiction_count=2,
                confidence_score=78,
                confidence_level="MODERATE",
                additional_info={"test": "data"}
            )
            
            # Verify file was created
            pattern_log_path = os.path.join(self.test_log_dir, PATTERN_ANALYSIS_LOG)
            self.assertTrue(os.path.exists(pattern_log_path))
            
            # Verify content
            with open(pattern_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("Test Result ID: 789", content)
                self.assertIn("Pattern Classification: decisive", content)
                self.assertIn("Consistency Score: 85.50", content)
                self.assertIn("Contradiction Count: 2", content)
                self.assertIn("Confidence Score: 78", content)
                self.assertIn("Confidence Level: MODERATE", content)
    
    def test_log_api_call_success(self):
        """Test that log_api_call logs successful API calls."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            logger = get_ai_logger('neuroapt.api_calls')
            
            with self.assertLogs('neuroapt.api_calls', level='INFO') as cm:
                log_api_call(
                    model="gpt-4o",
                    operation="test_operation",
                    profile_id=456,
                    response_time=2.5,
                    tokens_used=1500,
                    success=True
                )
            
            # Verify log message
            self.assertTrue(any("gpt-4o" in msg for msg in cm.output))
            self.assertTrue(any("test_operation" in msg for msg in cm.output))
            self.assertTrue(any("2.50s" in msg for msg in cm.output))
    
    def test_log_api_call_failure(self):
        """Test that log_api_call logs failed API calls."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            logger = get_ai_logger('neuroapt.api_calls')
            
            with self.assertLogs('neuroapt.api_calls', level='ERROR') as cm:
                log_api_call(
                    model="gpt-4o",
                    operation="test_operation",
                    success=False,
                    error="Timeout error"
                )
            
            # Verify error log message
            self.assertTrue(any("ERROR" in msg for msg in cm.output))
            self.assertTrue(any("Timeout error" in msg for msg in cm.output))
    
    def test_log_api_call_cache_hit(self):
        """Test that log_api_call correctly logs cache hits."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', self.test_log_dir):
            logger = get_ai_logger('neuroapt.api_calls')
            
            with self.assertLogs('neuroapt.api_calls', level='INFO') as cm:
                log_api_call(
                    model="gpt-4o",
                    operation="test_operation",
                    cache_hit=True,
                    success=True
                )
            
            # Verify cache hit in message
            self.assertTrue(any("Cache: HIT" in msg for msg in cm.output))


class TestLoggingErrorHandling(unittest.TestCase):
    """Test suite for logging error handling."""
    
    def test_log_ai_error_handles_file_write_failure(self):
        """Test that log_ai_error handles file write failures gracefully."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', '/invalid/path/that/does/not/exist'):
            # Should not raise exception
            try:
                log_ai_error(
                    component="Test",
                    operation="test",
                    error_type="Test",
                    error_message="Test"
                )
            except Exception as e:
                self.fail(f"log_ai_error raised exception: {e}")
    
    def test_log_pattern_analysis_handles_file_write_failure(self):
        """Test that log_pattern_analysis handles file write failures gracefully."""
        with patch('neuroapt.app.utils.logging_config.LOG_DIR', '/invalid/path/that/does/not/exist'):
            # Should not raise exception
            try:
                log_pattern_analysis(
                    test_result_id=123,
                    pattern_classification="test",
                    consistency_score=50.0,
                    contradiction_count=0,
                    confidence_score=50,
                    confidence_level="MODERATE"
                )
            except Exception as e:
                self.fail(f"log_pattern_analysis raised exception: {e}")


if __name__ == '__main__':
    unittest.main()
