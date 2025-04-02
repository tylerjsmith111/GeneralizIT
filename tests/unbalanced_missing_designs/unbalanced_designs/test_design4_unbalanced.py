import pytest
from tests.fixtures.design4_unbalanced_fixtures import test_design4_unbalanced

@pytest.mark.unbalanced
@pytest.mark.nested
def test_t_values(test_design4_unbalanced):
    """Tests the calculation of T values."""
    test_design4_unbalanced.set_tolerance(0.01).test__calculate_t_values()
    
@pytest.mark.unbalanced
@pytest.mark.nested
def test_variance_components(test_design4_unbalanced):
    """Tests the calculation of variance components."""
    test_design4_unbalanced.set_tolerance(0.01).test__calculate_variance()

@pytest.mark.unbalanced
@pytest.mark.nested
def test_anova_calculations(test_design4_unbalanced):
    """
    Tests the full ANOVA calculation for nested design.
    
    This comprehensive test verifies T values, variance components, 
    and the ANOVA table structure in the proper sequence.
    """
    # Use composite method for cleaner testing
    test_design4_unbalanced.set_tolerance(0.01).test_all_anova_components()

@pytest.mark.unbalanced
@pytest.mark.nested
def test_g_coefficients(test_design4_unbalanced):
    """Tests the calculation of G coefficients."""
    test_design4_unbalanced.set_tolerance(0.01).test__calculate_g_coeffs()