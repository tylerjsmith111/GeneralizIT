import pytest
from tests.fixtures.design1_missing_fixtures import test_design1_missing

@pytest.mark.missing
def test_t_values(test_design1_missing):
    """Tests the calculation of T values with missing data."""
    test_design1_missing.set_tolerance(0.01).test__calculate_t_values()
    
@pytest.mark.missing
def test_variance_components(test_design1_missing):
    """Tests the calculation of variance components with missing data."""
    test_design1_missing.set_tolerance(0.01).test__calculate_variance()

@pytest.mark.missing
def test_anova_calculations(test_design1_missing):
    """
    Tests the full ANOVA calculation for crossed person x item design with missing data.
    
    This comprehensive test verifies T values, variance components, 
    and the ANOVA table structure in the proper sequence.
    """
    # Use composite method for cleaner testing
    test_design1_missing.set_tolerance(0.01).test_all_anova_components()

@pytest.mark.missing
def test_g_coefficients(test_design1_missing):
    """Tests the calculation of G coefficients with missing data."""
    test_design1_missing.set_tolerance(0.01).test__calculate_g_coeffs()