from tests.fixtures.design4_fixtures import test_design4

# def test_get_unique_levels(design4):
#     """Test the `get_unique_levels` method of Design4."""
#
#     # Check levels for 'person', 'r', and 't'
#     assert design4.levels['person'] == 10  # 10 unique persons
#     assert design4.levels['r'] == 4  # 4 unique raters
#     assert design4.levels['t'] == 3  # 3 unique tasks
#
#
# def test__calculate_degrees_of_freedom(design4):
#     design4._calculate_degrees_of_freedom()
#
#     # Check that degrees of freedom are calculated
#     assert hasattr(design4, 'deg_freedom'), "Degrees of freedom should be calculated."
#
#     # Verify degrees of freedom
#     deg_freedom = {
#         'person': 9,
#         't': 2,
#         'r:t': 9,
#         'person x t': 18,
#         'person x (r:t)': 81
#     }
#
#     assert design4.deg_freedom == deg_freedom
#
#
# def test__calculate_t_values(design4):
#     design4._calculate_T_values()
#
#     # Check that T values are calculated
#     assert hasattr(design4, 'T'), "T values should be calculated."
#
#     # Verify T values
#     T_values = {
#         'person': 2800.1667,
#         't': 2755.7000,
#         'r:t': 2835.4000,
#         'person x t': 2931.5000,
#         'person x (r:t)': 3204.0000,
#         'u': 2707.5,
#     }
#
#     # Check T Values to 1 decimal place
#     for key, value in T_values.items():
#         assert round(design4.T[key], 1) == round(value, 1)
#
#
# def test__calculate_sums_of_squares(design4):
#     # Sum of Squares requires T values to be calculated first
#     design4._calculate_T_values()
#
#     design4._calculate_sums_of_squares()
#
#     # Check that SS values are calculated
#     assert hasattr(design4, 'SS'), "Sum of Squares values should be calculated."
#
#     # Verify SS values
#     SS_values = {
#         'person': 92.6667,
#         't': 48.2000,
#         'r:t': 79.7000,
#         'person x t': 83.1333,
#         'person x (r:t)': 192.8000,
#     }
#
#     # Check SS Values to 1 decimal place
#     for key, value in SS_values.items():
#         assert round(design4.SS[key], 1) == round(value, 1)
#
# def test__calculate_mean_squares(design4):
#     # All previous calculations are required
#     design4._calculate_degrees_of_freedom()
#     design4._calculate_T_values()
#     design4._calculate_sums_of_squares()
#
#     design4._calculate_mean_squares()
#
#     # Check that MS values are calculated
#     assert hasattr(design4, 'MS'), "Mean Squares values should be calculated."
#
#     # Verify MS values
#     MS_values = {
#         'person': 10.2963,
#         't': 24.1000,
#         'r:t': 8.8556,
#         'person x t': 4.6185,
#         'person x (r:t)': 2.3802,
#     }
#
#     # Check MS Values to 1 decimal place
#     for key, value in MS_values.items():
#         assert round(design4.MS[key], 1) == round(value, 1)
#
# def test_calculate_anova(design4):
#     design4.calculate_anova()
#
#     # Check that ANOVA table exists
#     assert hasattr(design4, 'anova_table'), "ANOVA table should be calculated."
#
#     # Verify dimensions of the ANOVA table
#     assert design4.anova_table.shape[0] == 5  # Five sources of variation
#
#     # Check column names in ANOVA table
#     expected_columns = ['Source of Variation', 'Degrees of Freedom', 'Sum of Squares', 'Mean Square',
#                         'Variance Component']
#     assert list(design4.anova_table.columns) == expected_columns
#
#
# def test__calculate_variance(design4):
#     # All previous calculations are required
#     design4._calculate_degrees_of_freedom()
#     design4._calculate_T_values()
#     design4._calculate_sums_of_squares()
#     design4._calculate_mean_squares()
#
#     design4._calculate_variance()
#
#     # Check that variance values are calculated
#     assert hasattr(design4, 'variances'), "Variance values should be calculated."
#
#     # Verify variance values
#     variances = {
#         'person': 0.4731,
#         't': 0.3252,
#         'r:t': 0.6475,
#         'person x t': 0.5596,
#         'person x (r:t)': 2.3802,
#     }
#
#     # Check variance values to 2 decimal place
#     for key, value in variances.items():
#         assert round(design4.variances[key], 2) == round(value, 2)
#
#
#
# def test__calculate_g_coeffs(design4):
#     design4.calculate_anova()  # ANOVA must be calculated first
#
#     g_coeff_df = design4._calculate_g_coeffs()
#
#     # Check the resulting DataFrame
#     assert not g_coeff_df.empty, "G coefficient DataFrame should not be empty."
#     expected_columns = ['Source of Variation', 'Generalized Over Fixed', 'Generalized Over Random', 'rho^2', 'phi^2']
#     assert list(g_coeff_df.columns) == expected_columns
#
#     # check the values of the rho^2 and phi^2 for person
#     assert round(g_coeff_df.loc[g_coeff_df['Source of Variation'] == 'person', 'rho^2'].values[0], 2) == 0.55
#     assert round(g_coeff_df.loc[g_coeff_df['Source of Variation'] == 'person', 'phi^2'].values[0], 2) == 0.46


def test_class_construction(test_design4):
    """Test the construction of Design4 by checking the levels."""
    test_design4.test_get_unique_levels()

def test_anova_calculations(test_design4):
    """
    Tests the various constructions of Design4.
    This includes the calculation of degrees of freedom, T values, sums of squares, mean squares, variance, and ANOVA table.
    """
    test_design4.test__calculate_degrees_of_freedom()
    test_design4.test__calculate_t_values()
    test_design4.test__calculate_sums_of_squares()
    test_design4.test__calculate_mean_squares()
    test_design4.test__calculate_variance()
    test_design4.test_calculate_anova()

def test_g_coefficients(test_design4):
    """Tests the calculation of G coefficients."""
    test_design4.test__calculate_g_coeffs()
