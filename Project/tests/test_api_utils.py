import pytest
import requests

from todo.utils.api_utils import get_random

# Pick a sample integer that our mock will return
RANDOM_NUMBER = 42

@pytest.fixture
def mock_random_org(mocker):
    """
    Patch requests.get so that it returns a fake response
    whose .text is our RANDOM_NUMBER.
    """
    mock_response = mocker.Mock()
    mock_response.text = str(RANDOM_NUMBER)
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response

def test_get_random(mock_random_org):
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

def test_get_random_request_failure(mocker):
    """Test handling of a generic request failure."""
    mocker.patch("requests.get",
                 side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        get_random(5)

def test_get_random_timeout(mocker):
    """Test handling of a timeout."""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random(5)

def test_get_random_invalid_response(mock_random_org):
    """Test handling of a non-integer response."""
    mock_random_org.text = "not_an_int"
    with pytest.raises(ValueError, match="Invalid response from random.org: 'not_an_int'"):
        get_random(5)
