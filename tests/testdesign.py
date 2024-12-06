import numpy as np

class TestDesign:
    def __init__(
            self,
            design,
            levels_dict,
            deg_freedom_dict,
            t_values_dict,
            ss_values_dict,
            ms_values_dict,
            variances_dict,
            rho_dict,
            phi_dict
    ):
        """
        TestDesign is the base class for testing various designs on synthetic data to confirm
        proper functionality for calculating necessary G Theory components.
        """
        self.design = design

        # These dictionaries are used to verify the calculations
        self.levels_dict = levels_dict
        self.deg_freedom_dict = deg_freedom_dict
        self.t_values_dict = t_values_dict
        self.ss_values_dict = ss_values_dict
        self.ms_values_dict = ms_values_dict
        self.variances_dict = variances_dict
        self.rho_dict = rho_dict
        self.phi_dict = phi_dict


    def test_get_unique_levels(self):
        """Test the `get_unique_levels` method of Design."""
        for key, value in self.levels_dict.items():
            assert self.design.levels[key] == value, f"Unique levels for {key} should be {value}."

    def test__calculate_degrees_of_freedom(self):
        """Check that degrees of freedom are calculated and are correct."""
        self.design._calculate_degrees_of_freedom()

        # Check that degrees of freedom is not {}
        assert self.design.deg_freedom, "Degrees of freedom should be calculated."

        # Verify degrees of freedom
        for key, value in self.deg_freedom_dict.items():
            assert self.design.deg_freedom[key] == value, f"Degrees of freedom for {key} should be {value}."

    def test__calculate_t_values(self):
        """Checks the T value calculations needed for Sum of Squares"""

        self.design._calculate_T_values()

        # Check that T values are calculated
        assert self.design.T, "T values should be calculated."

        # Verify T values
        for key, value in self.t_values_dict.items():
            assert np.isclose(self.design.T[key], value, atol=.01), f"T value for {key} should be {value}, got {self.design.T[key]}."


    def test__calculate_sums_of_squares(self):
        """Checks the Sum of Squares calculations"""
        self.design._calculate_sums_of_squares()

        # Check that SS values are calculated
        assert self.design.SS, "Sum of Squares values should be calculated."

        # Verify SS values
        for key, value in self.ss_values_dict.items():
            assert np.isclose(self.design.SS[key], value, atol=.01), f"Sum of Squares for {key} should be {value}, got {self.design.SS[key]}."

    def test__calculate_mean_squares(self):
        """Checks the Mean Squares calculations"""
        self.design._calculate_mean_squares()

        # Check that MS values are calculated
        assert self.design.MS, "Mean Squares values should be calculated."

        # Verify MS values
        for key, value in self.ms_values_dict.items():
            assert np.isclose(self.design.MS[key], value, atol=.01), f"Mean Squares for {key} should be {value}, got {self.design.MS[key]}."

    def test__calculate_variance(self):
        """Checks the variance calculations"""
        self.design._calculate_variance()

        # Check that variance values are calculated
        assert self.design.variances, "Variance values should be calculated."

        # Verify variance values
        for key, value in self.variances_dict.items():
            assert np.isclose(self.design.variances[key], value, atol=.01), f"Variance for {key} should be {value}.\n{np.abs(round(self.design.variances[key], 2) - round(value, 2))}"

    def test_calculate_anova(self):
        """Checks the ANOVA table design, calculations are checked above"""
        self.design.calculate_anova()

        # Check that ANOVA table is not None
        assert self.design.anova_table is not None, "ANOVA table should be calculated."

        # Verify ANOVA table has expected columns
        expected_columns = [
            'Source of Variation',
            'Degrees of Freedom',
            'Sum of Squares',
            'Mean Square',
            'Variance Component'
        ]

        assert list(self.design.anova_table.columns) == expected_columns, "ANOVA table should have the expected columns."

    def test__calculate_g_coeffs(self):
        """Checks the G coefficient calculations"""
        self.design.calculate_anova()  # ANOVA must be calculated first

        # check to make sure that 'Total' is not in the source of variation
        if 'Total' in self.design.variances.keys():
            self.design.variances.pop('Total')

        g_coeff_df = self.design._calculate_g_coeffs()

        # Check the resulting DataFrame
        assert not g_coeff_df.empty, "G coefficient DataFrame should not be empty."

        # Verify structure of the DataFrame
        expected_columns = ['Source of Variation', 'Generalized Over Fixed', 'Generalized Over Random', 'rho^2',
                            'phi^2']
        for column in expected_columns:
            assert column in g_coeff_df.columns, f"Column {column} should be in the DataFrame."

        # Verify G coefficients
        for key, value in self.rho_dict.items():
            mask = (g_coeff_df['Source of Variation'] == key) & (g_coeff_df['Generalized Over Fixed'] == '---')
            rho_value = g_coeff_df.loc[mask, 'rho^2'].values[0]
            assert np.isclose(rho_value, value, atol=0.01), f"rho^2 for {key} should be {value}, but got {rho_value}."

        for key, value in self.phi_dict.items():
            mask = (g_coeff_df['Source of Variation'] == key) & (g_coeff_df['Generalized Over Fixed'] == '---')
            phi_value = g_coeff_df.loc[mask, 'phi^2'].values[0]
            assert np.isclose(phi_value, value, atol=0.01), f"phi^2 for {key} should be {value}, but got {phi_value}."
