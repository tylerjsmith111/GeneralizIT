from tests.fixtures.design1_fixtures import test_design1

def test_class_construction(test_design1):
    """Test the construction of Design2 by checking the levels."""
    test_design1.test_get_unique_levels()

def test_anova_calculations(test_design1):
    """
    Tests the various constructions of Design2.
    This includes the calculation of degrees of freedom, T values, sums of squares, mean squares, variance, and ANOVA table.
    """
    test_design1.test__calculate_degrees_of_freedom()
    test_design1.test__calculate_t_values()
    test_design1.test__calculate_sums_of_squares()
    test_design1.test__calculate_mean_squares()
    test_design1.test__calculate_variance()
    test_design1.test_calculate_anova()

def test_g_coefficients(test_design1):
    """Tests the calculation of G coefficients."""
    test_design1.test__calculate_g_coeffs()