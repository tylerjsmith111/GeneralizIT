import pytest
from tests.fixtures.design2_fixtures import test_design2

@pytest.mark.balanced
@pytest.mark.nested
def test_t_values(test_design2):
    """Tests the calculation of T values."""
    test_design2.set_tolerance(0.01).test__calculate_t_values()

@pytest.mark.balanced
@pytest.mark.nested
def test_variance_components(test_design2):
    """Tests the calculation of variance components."""
    test_design2.set_tolerance(0.01).test__calculate_variance()

@pytest.mark.balanced
@pytest.mark.nested
def test_anova_calculations(test_design2):
    """
    Tests the full ANOVA calculation for nested design.
    
    This comprehensive test verifies T values, variance components, 
    and the ANOVA table structure in the proper sequence.
    """
    # Use composite method for cleaner testing
    test_design2.set_tolerance(0.01).test_all_anova_components()

@pytest.mark.balanced
@pytest.mark.nested
def test_g_coefficients(test_design2):
    """Tests the calculation of G coefficients."""
    test_design2.set_tolerance(0.01).test__calculate_g_coeffs()
    
@pytest.mark.balanced
@pytest.mark.nested
def test_d_coefficients(test_design2):
    """Tests the calculation of G coefficients."""
    test_design2.set_tolerance(0.01).test__calculate_d_study(d_study_design={'person': [10], 'item': [8]}, utils=True)
    
@pytest.mark.balanced
@pytest.mark.nested
def test_confidence_intervals(test_design2):
    """Tests the calculation of confidence intervals."""
    test_design2.set_tolerance(0.01).test__calculate_confidence_intervals()

