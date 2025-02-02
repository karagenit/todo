import pytest
from repeat import validate_single_repeat, validate_repeat, next_repeat_date

def test_validate_single_repeat():
    assert validate_single_repeat('*', 1, 31) == True
    assert validate_single_repeat('1', 1, 31) == True
    assert validate_single_repeat('1,15', 1, 31) == True
    assert validate_single_repeat('1-15', 1, 31) == True
    assert validate_single_repeat('*/5', 1, 31) == True
    assert validate_single_repeat('32', 1, 31) == False
    assert validate_single_repeat('0', 1, 31) == False
    assert validate_single_repeat('1-32', 1, 31) == False
    assert validate_single_repeat('invalid', 1, 31) == False

def test_validate_repeat():
    assert validate_repeat('* * * 0 C') == True
    assert validate_repeat('1 1 0 0 C') == True
    assert validate_repeat('1-15 */2 0,1,2 30 S') == True
    assert validate_repeat('invalid') == False
    assert validate_repeat('* * * 1000 C') == False
    assert validate_repeat('* * * 0 X') == False

def test_next_repeat_date():
    # Add tests once the function is implemented
    pass
