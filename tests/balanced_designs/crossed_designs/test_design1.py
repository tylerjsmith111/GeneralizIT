import pytest
from tests.fixtures.design1_fixtures import test_design1

@pytest.mark.crossed
@pytest.mark.balanced
def test_t_values(test_design1):
    """Tests the calculation of T values."""
    test_design1.set_tolerance(0.01).test__calculate_t_values()

@pytest.mark.crossed
@pytest.mark.balanced
def test_variance_components(test_design1):
    """Tests the calculation of variance components."""
    test_design1.set_tolerance(0.01).test__calculate_variance()

@pytest.mark.crossed
@pytest.mark.balanced
def test_anova_calculations(test_design1):
    """
    Tests the full ANOVA calculation for crossed person x item design.
    
    This comprehensive test verifies T values, variance components, 
    and the ANOVA table structure in the proper sequence.
    """
    # Use composite method for cleaner testing
    test_design1.set_tolerance(0.01).test_all_anova_components()

@pytest.mark.crossed
@pytest.mark.balanced
def test_g_coefficients(test_design1):
    """Tests the calculation of G coefficients."""
    test_design1.set_tolerance(0.01).test__calculate_g_coeffs()
    
@pytest.mark.crossed
@pytest.mark.balanced
def test_d_coefficients(test_design1):
    """Tests the calculation of D coefficients."""
    test_design1.set_tolerance(0.01).test__calculate_d_study(d_study_design={'person': [10], 'item': [5, 10, 15, 20]})
    
@pytest.mark.crossed
@pytest.mark.balanced
def test_confidence_intervals(test_design1):
    """Tests the calculation of confidence intervals."""
    test_design1.set_tolerance(0.01).test__calculate_confidence_intervals()