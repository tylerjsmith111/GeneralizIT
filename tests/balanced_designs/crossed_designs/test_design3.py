import pytest
from tests.fixtures.design3_fixtures import test_design3
from tests.fixtures.design3_fixed_fixtures import test_design3_fixed

@pytest.mark.crossed
@pytest.mark.balanced
def test_t_values(test_design3):
    """Tests the calculation of T values."""
    test_design3.set_tolerance(0.01).test__calculate_t_values()

@pytest.mark.crossed
@pytest.mark.balanced
def test_variance_components(test_design3):
    """Tests the calculation of variance components."""
    test_design3.set_tolerance(0.01).test__calculate_variance()

@pytest.mark.crossed
@pytest.mark.balanced
def test_anova_calculations(test_design3):
    """
    Tests the full ANOVA calculation for crossed design3.
    
    This comprehensive test verifies T values, variance components, 
    and the ANOVA table structure in the proper sequence.
    """
    # Use composite method for cleaner testing
    test_design3.set_tolerance(0.01).test_all_anova_components()

@pytest.mark.crossed
@pytest.mark.balanced
def test_g_coefficients(test_design3):
    """Tests the calculation of Random G coefficients."""
    test_design3.set_tolerance(0.01).test__calculate_g_coeffs()
    
@pytest.mark.crossed
@pytest.mark.balanced
def test_fixed_g_coefficients(test_design3):
    """Tests the calculation of Random G coefficients with items fixed."""
    test_design3.set_tolerance(0.01).test__calculate_g_coeffs(fixed_facets=['i'])
    
@pytest.mark.crossed
@pytest.mark.balanced
def test_d_coefficients(test_design3):
    """Tests the calculation of D coefficients."""
    test_design3.set_tolerance(0.01).test__calculate_d_study(d_study_design={'person': [10], 'i': [4], 'o': [2]}, utils=True)
    
@pytest.mark.crossed
@pytest.mark.balanced
def test_confidence_intervals(test_design3):
    """Tests the calculation of confidence intervals."""
    test_design3.set_tolerance(0.01).test__calculate_confidence_intervals()