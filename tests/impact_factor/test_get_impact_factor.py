import pytest
from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor


def test_get_impact_factor_existing_issn():
    # Setup: Mock the impact_factor_df DataFrame to return a sample row
    issn = '0007-9235'
    expected_result = 286.13
    actual_result = get_impact_factor(issn)
    print(actual_result)
    # Assertion: Check that the function returns the expected result
    assert actual_result == expected_result

def test_get_impact_factor_non_existing_issn():
    # Setup: Mock the impact_factor_df DataFrame to be empty
    issn = '1234-5678'

    # Action: Call the function
    result = get_impact_factor(issn)

    # Assertion: Check that the function returns None for non-existing ISSN
    assert result is None

if __name__ == "__main__":
    pytest.main([__file__])
