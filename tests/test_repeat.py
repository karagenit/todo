import pytest
from datetime import datetime, timedelta
from repeat import next_repeat_date, matches_repeat_field
from repeat_validation import validate_single_repeat, validate_repeat

def test_validate_single_repeat():
    assert validate_single_repeat('*', 1, 31) == True
    assert validate_single_repeat('1', 1, 31) == True
    assert validate_single_repeat('1,15', 1, 31) == True
    assert validate_single_repeat('1-15', 1, 31) == True
    assert validate_single_repeat('*/5', 1, 31) == True
    assert validate_single_repeat('1-10,20-28,31', 1, 31) == True
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
    assert validate_repeat('* * 9 0 C') == False
    assert validate_repeat('* 13 * 0 C') == False
    assert validate_repeat('32 * * 0 C') == False

def test_matches_repeat_field():
    # Test wildcard
    assert matches_repeat_field('*', 5) == True
    assert matches_repeat_field('*', 0) == True    
    # Test single values
    assert matches_repeat_field('5', 5) == True
    assert matches_repeat_field('5', 6) == False
    # Test comma-separated lists
    assert matches_repeat_field('1,5,10', 5) == True
    assert matches_repeat_field('1,5,10', 7) == False
    # Test ranges
    assert matches_repeat_field('1-5', 3) == True
    assert matches_repeat_field('1-5', 6) == False
    # Test step values
    assert matches_repeat_field('*/2', 4) == True
    assert matches_repeat_field('*/2', 3) == False    
    # Test complex combinations
    assert matches_repeat_field('1-5,7,9-11', 7) == True
    assert matches_repeat_field('1-5,7,9-11', 10) == True
    assert matches_repeat_field('1-5,7,9-11', 6) == False

def test_next_repeat_date():
    # Test completion-based repeat (C)
    assert next_repeat_date(datetime(2023, 1, 1), datetime(2023, 1, 15), '* * * 7 C') == datetime(2023, 1, 22)
    # Test start-based repeat (S)
    assert next_repeat_date(datetime(2023, 1, 1), datetime(2023, 1, 15), '* * * 7 S') == datetime(2023, 1, 8)
    # Test specific day of month (15th of any month)
    assert next_repeat_date(datetime(2023, 1, 1), datetime(2023, 1, 1), '15 * * 0 C') == datetime(2023, 1, 15)
    # Test specific month (only March)
    assert next_repeat_date(datetime(2023, 1, 1), datetime(2023, 1, 1), '* 3 * 0 C') == datetime(2023, 3, 1)
    # Test specific day of week (only Sundays - 0)
    assert next_repeat_date(datetime(2023, 1, 1), datetime(2023, 1, 2), '* * 0 0 C') == datetime(2023, 1, 8)
    # Test invalid repeat string
    assert next_repeat_date(datetime(2023, 1, 1), datetime(2023, 1, 2), 'invalid') == None
