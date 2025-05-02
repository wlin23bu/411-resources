import pytest
import requests
import os

from todo.utils.api_utils import get_random

# Pick a sample integer that our mock will return
RANDOM_NUMBER = 42

@pytest.fixture
def mock_random_org(mocker):
    """
    Patch requests.get so that it returns a fake response
    whose .text is our RANDOM_NUMBER.
    """
    os.environ["USE_FALLBACK_RNG"] = "0"
    
    mock_response = mocker.Mock()
    mock_response.text = str(RANDOM_NUMBER)
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

@pytest.fixture
def restore_env():
    """Restore environment variables after test."""
    old_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(old_env)

def test_get_random(mock_random_org, restore_env):
    """Test retrieving a random integer from random.org."""
    n = 100
    result = get_random(n)
    #should parse our mocked text into the integer 42
    assert result == RANDOM_NUMBER, f"Expected {RANDOM_NUMBER}, but got {result}"

    #should have called the integer ith max=n
    expected_url = (
        "https://www.random.org/integers/"
        "?num=1&min=1&max=100&col=1&base=10&format=plain&rnd=new"
    )
    requests.get.assert_called_once_with(expected_url, timeout=5)

def test_get_random_request_failure(mocker, restore_env):
    """Test that request failures use fallback RNG."""
    os.environ["USE_FALLBACK_RNG"] = "0"
    
    # monkey patch simulations:
    mocker.patch("random.randint", return_value=3)
    mocker.patch("requests.get", 
                 side_effect=requests.exceptions.RequestException("Connection error"))
    
    # Should use fallback RNG and return the mocked value
    result = get_random(5)
    assert result == 3, "Should use fallback RNG which returns 3"

def test_get_random_timeout(mocker, restore_env):
    """Test that timeouts use fallback RNG."""
    os.environ["USE_FALLBACK_RNG"] = "0"
    
    # Patch random.randint to return a predictable value
    mocker.patch("random.randint", return_value=4)
    
    # Simulate timeout
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    
    # Should use fallback RNG and return the mocked value
    result = get_random(5)
    assert result == 4, "Should use fallback RNG which returns 4"

def test_get_random_invalid_response(mock_random_org, restore_env):
    """Test handling of a non-integer response."""
    mock_random_org.text = "not_an_int"
    with pytest.raises(ValueError, match="Invalid response from random.org: 'not_an_int'"):
        get_random(5)

def test_get_random_fallback(mocker, restore_env):
    """Test that fallback RNG is used when enabled."""
    os.environ["USE_FALLBACK_RNG"] = "1"
    
    # Patch random.randint to return a predictable value
    mocker.patch("random.randint", return_value=7)
    
    mock_response = mocker.Mock()
    mock_response.text = "999"  # should never be used
    mocker.patch("requests.get", return_value=mock_response)
    
    result = get_random(10)
    assert result == 7, "Should use fallback RNG which returns 7"
    
    requests.get.assert_not_called()
