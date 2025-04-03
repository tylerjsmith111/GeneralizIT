from tests.fixtures.design5_fixtures import test_design5
import pytest
    
@pytest.mark.skip
def test_t_values(test_design5):
    """Tests the calculation of T values."""
    test_design5.set_tolerance(0.01).test__calculate_t_values()

@pytest.mark.skip
def test_variance_components(test_design5):
    """Tests the calculation of variance components."""
    test_design5.set_tolerance(0.01).test__calculate_variance()

@pytest.mark.skip
def test_anova_calculations(test_design5):
    """
    Tests the full ANOVA calculation for nested design.
    
    This comprehensive test verifies T values, variance components, 
    and the ANOVA table structure in the proper sequence.
    """
    # Use composite method for cleaner testing
    test_design5.set_tolerance(0.01).test_all_anova_components()

@pytest.mark.skip
def test_g_coefficients(test_design5):
    """Tests the calculation of G coefficients."""
    test_design5.set_tolerance(0.01).test__calculate_g_coeffs()