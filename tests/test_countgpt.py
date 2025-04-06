"""Tests for the countgpt package."""
import pytest
from click.testing import CliRunner
from countgpt.cli import main
from countgpt.models import count_tokens, count_tokens_in_file
from pathlib import Path


def test_count_tokens():
    """Test the token counting function."""
    # Simple test case
    assert count_tokens("Hello, world!") > 0
    
    # Empty string
    assert count_tokens("") == 0
    
    # Test with different models
    text = "This is a test of token counting"
    model1_count = count_tokens(text, "cl100k_base")
    model2_count = count_tokens(text, "p50k_base")
    # Different models may produce different token counts
    assert isinstance(model1_count, int)
    assert isinstance(model2_count, int)
    
    # Test with invalid model
    with pytest.raises(ValueError):
        count_tokens("test", "invalid_model_name")


@pytest.fixture
def sample_file(tmp_path):
    """Create a sample file for testing."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("This is a sample text file for testing token counting.")
    return file_path


def test_count_tokens_in_file(sample_file):
    """Test counting tokens in a file."""
    result = count_tokens_in_file(sample_file)
    assert result["tokens"] > 0
    assert result["characters"] > 0
    assert result["file"] == str(sample_file)
    assert result["model"] == "cl100k_base"
    
    # Test with nonexistent file
    with pytest.raises(FileNotFoundError):
        count_tokens_in_file("nonexistent_file.txt")


def test_cli():
    """Test the command line interface."""
    runner = CliRunner()
    
    # Test help output
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Count tokens in text files" in result.output
    
    # Test with piped input
    result = runner.invoke(main, input="Hello, world!")
    assert result.exit_code == 0
    assert result.output.strip().isdigit()
    
    # Test verbose output
    result = runner.invoke(main, ["-v"], input="Test verbose output")
    assert result.exit_code == 0
    assert "Model:" in result.output
    assert "Token count:" in result.output
    assert "Character count:" in result.output