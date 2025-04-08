import pytest
from filter_args import FilterArgs

def test_filter_args_default_initialization():
    """Test initialization with empty request args."""
    filter_args = FilterArgs({})
    assert filter_args.search == ''
    assert filter_args.hide_children is True
    assert filter_args.show_future is False
    assert filter_args.priority is None
    assert filter_args.count == 5

def test_filter_args_custom_initialization():
    """Test initialization with custom request args."""
    request_args = {
        'search': 'test query',
        'hide_children': False,
        'show_future': True,
        'priority': '2',
        'count': '10'
    }
    filter_args = FilterArgs(request_args)
    assert filter_args.search == 'test query'
    assert filter_args.hide_children is False
    assert filter_args.show_future is True
    assert filter_args.priority == 2  # Should be converted to int
    assert filter_args.count == 10    # Should be converted to int

def test_to_url_params_empty():
    """Test URL parameter generation with default values. Most are none/blank but count is 5 by default so it's always included in params"""
    filter_args = FilterArgs({})
    assert filter_args.to_url_params() == '?count=5'

def test_to_url_params_with_values():
    """Test URL parameter generation with custom values."""
    request_args = {
        'search': 'test query',
        'show_future': True,
        'priority': '1',
        'count': '15'
    }
    filter_args = FilterArgs(request_args)
    url_params = filter_args.to_url_params()
    
    # Check that all expected parameters are in the URL
    assert '?' in url_params
    assert 'search=test+query' in url_params
    assert 'show_future=on' in url_params
    assert 'priority=1' in url_params
    assert 'count=15' in url_params

def test_to_url_params_encoding():
    """Test proper URL encoding of special characters."""
    request_args = {
        'search': 'test & query with spaces',
    }
    filter_args = FilterArgs(request_args)
    url_params = filter_args.to_url_params()
    
    assert 'search=test+%26+query+with+spaces' in url_params
