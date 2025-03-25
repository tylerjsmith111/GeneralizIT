"""
Base test infrastructure for G-theory designs.

This module provides a common test framework for verifying calculations
in different generalizability theory design implementations.
"""

import numpy as np
import pandas as pd
from generalizit.design import Design
from typing import Dict, Any, Union, Optional, List

class DesignTestBase:
    """
    Base class for testing G-theory design implementations.
    
    This class provides common test methods for verifying calculations
    across different design types, ensuring consistent validation of
    G-theory components including degrees of freedom, variance components,
    and G-coefficients.
    
    Attributes:
        design: The design instance being tested
        levels_df: Expected DataFrame of unique level coefficients
        deg_freedom_dict: Expected degrees of freedom for each component
        t_values_dict: Expected T values for sum of squares calculations
        ss_values_dict: Expected sum of squares values
        ms_values_dict: Expected mean squares values
        variances_dict: Expected variance component values
        rho_dict: Expected rho^2 (relative) coefficient values
        phi_dict: Expected phi^2 (absolute) coefficient values
    """
    def __init__(
            self,
            design: Design,
            levels_df: pd.DataFrame,
            t_values_dict: Dict[str, float],
            variances_dict: Dict[str, float],
            rho_dict: Dict[str, float],
            phi_dict: Dict[str, float]
    ):
        """
        Initialize the base test class with the specified design and expected values.
        
        Args:
            design: The design instance being tested
            expected_levels_coeffs: Expected DataFrame of unique level coefficients
            t_values_dict: Expected T values for sum of squares calculations
            variances_dict: Expected variance component values
            rho_dict: Expected rho^2 (relative) coefficient values
            phi_dict: Expected phi^2 (absolute) coefficient values
        """

        self.design = design
        self.expected_levels_coeffs = levels_df
        self.t_values_dict = t_values_dict
        self.variances_dict = variances_dict
        self.rho_dict = rho_dict
        self.phi_dict = phi_dict
        
        # Default test parameters
        self.atol = 0.01
        
    # ---- Configuration Methods ----
    
    def set_tolerance(self, atol: float = 0.01) -> 'DesignTestBase':
        """Set the absolute tolerance for numerical comparisons."""
        self.atol = atol
        return self
    
    # ---- Utility Methods ----
    
    def _assert_dict_values(self, actual: Dict, expected: Dict, 
                           msg_prefix: str, atol: Optional[float] = None) -> 'DesignTestBase':
        """Helper method to assert dictionary values match within tolerance."""
        atol = atol or self.atol
        for key, value in expected.items():
            assert np.isclose(actual[key], value, atol=atol), \
                f"{msg_prefix} for {key} should be {value}, got {actual[key]}."
        return self

    # ---- Basic Structure Tests ----
    def test__calculate_levels_coeffs(self):
        """
        Test the levels coefficients calculation.
        
        This method verifies that the levels coefficients are correctly calculated
        by comparing against expected values.
        
        Returns:
            self: For method chaining
        """
        # Call the method being tested if needed
        if self.design.levels_coeffs.empty:
            self.design._calculate_levels_coeffs()
        
        # Check that levels_coeffs DataFrame exists and is not empty
        assert not self.design.levels_coeffs.empty, "Levels coefficients DataFrame should not be empty."
        
        # Check that the DataFrame has the expected shape
        expected_shape = self.expected_levels_coeffs.shape
        actual_shape = self.design.levels_coeffs.shape
        assert actual_shape == expected_shape, f"Levels coefficients DataFrame should have shape {expected_shape}, but got {actual_shape}."
        
        # Check that all expected rows and columns exist
        for idx in self.expected_levels_coeffs.index:
            assert idx in self.design.levels_coeffs.index, f"Expected row index '{idx}' not found in levels coefficients DataFrame."
        
        for col in self.expected_levels_coeffs.columns:
            assert col in self.design.levels_coeffs.columns, f"Expected column '{col}' not found in levels coefficients DataFrame."
        
        # Compare values with tolerance
        for idx in self.expected_levels_coeffs.index:
            for col in self.expected_levels_coeffs.columns:
                expected = self.expected_levels_coeffs.loc[idx, col]
                actual = self.design.levels_coeffs.loc[idx, col]
                assert np.isclose(actual, expected, atol=self.atol), \
                    f"Levels coefficient for {idx},{col} should be {expected}, got {actual}."
        
        return self  # Allow method chaining

    
    # ---- ANOVA Component Tests ----
    def test__calculate_t_values(self):
        """
        Test the calculation of T values (uncorrected sum of squares).
        
        This method verifies that T values are correctly calculated for each facet
        by comparing against expected values.
        
        Returns:
            self: For method chaining
        """
        # Call the method being tested
        self.design._calculate_T_values()
        
        # Check that T values dictionary is not empty
        assert self.design.T, "T values dictionary should not be empty."
        
        # Check that all expected components exist in actual results
        for key in self.t_values_dict:
            assert key in self.design.T, f"T value for {key} not found in results."
        
        # Use helper method to verify values
        return self._assert_dict_values(
            actual=self.design.T,
            expected=self.t_values_dict,
            msg_prefix="T value",
            atol=self.atol
        )
        
        
    def test__calculate_variance(self, skip_components=None):
        """
        Checks the variance calculations against expected values.
        
        Args:
            skip_components: Optional list of components to skip in verification
        
        Returns:
            self: For method chaining
        """
        # Check if T values exist, if not calculate them
        if not hasattr(self.design, 'T') or not self.design.T:
            self.design._calculate_T_values()
        
        # Call the method being tested (We must first create the variance coefficients table)
        self.design._create_variance_coefficients_table()
        self.design._calculate_variance()
        
        # Check that anova_table is created and has Variance column
        assert self.design.anova_table is not None, "ANOVA table should be calculated."
        assert 'Variance' in self.design.anova_table.columns, "ANOVA table should contain Variance column."
        
        # Extract variances from anova_table into a dictionary for comparison
        actual_variances = {}
        for idx, row in self.design.anova_table.iterrows():
            actual_variances[idx] = row['Variance']
        
        # Skip any components if specified
        expected_variances = self.variances_dict.copy()
        if skip_components:
            for component in skip_components:
                if component in expected_variances:
                    expected_variances.pop(component)
        
        # Check that all expected components exist in actual results
        for key in expected_variances:
            assert key in actual_variances, f"Variance component for {key} not found in results. {actual_variances}"
        
        # Use helper method to verify values
        return self._assert_dict_values(
            actual=actual_variances, 
            expected=expected_variances,
            msg_prefix="Variance component",
            atol=self.atol
        )
    
    def test_calculate_anova(self):
        """
        Test the ANOVA table structure and existence.
        
        This method verifies that the ANOVA table is properly created
        and contains the expected columns. The individual calculations
        are verified in other test methods.
        
        Returns:
            self: For method chaining
        """
        self.design.calculate_anova()

        # Check that ANOVA table is not None
        assert self.design.anova_table is not None, "ANOVA table should be calculated."

        # Verify ANOVA table has expected columns
        expected_columns = ['T', 'Variance']
        assert all(col in self.design.anova_table.columns for col in expected_columns), \
            f"ANOVA table should have columns {expected_columns}"

        return self # Allow method chaining
    
    # ---- G Coefficient Tests ----
    def test__calculate_g_coeffs(self):
        """
        Test the G-coefficient calculations.
        
        This method verifies that the G-coefficients (rho^2 and phi^2) are correctly calculated
        by comparing against expected values provided in the test setup.
        
        Returns:
            self: For method chaining
        """
        if self.design.anova_table.empty:
            # ANOVA must be calculated first
            self.design.calculate_anova()

        # check to make sure that 'Total' is not in the source of variation
        if 'Total' in self.design.variances.keys():
            self.design.variances.pop('Total')

        # Call the method being tested
        self.design.g_coeffs()

        # Check the resulting DataFrame
        assert not self.design.g_coeffs_table.empty, "G coefficient DataFrame should not be empty."

        # Verify structure of the DataFrame
        expected_columns = ['rho^2', 'phi^2']
        for column in expected_columns:
            assert column in self.design.g_coeffs_table.columns, f"Column {column} should be in the DataFrame."

        # Verify G coefficients using the DataFrame's index as key
        for key, value in self.rho_dict.items():
            rho_value = self.design.g_coeffs_table.loc[key, 'rho^2']
            assert np.isclose(rho_value, value, atol=0.01), \
            f"rho^2 for {key} should be {value}, but got {rho_value}."

        for key, value in self.phi_dict.items():
            phi_value = self.design.g_coeffs_table.loc[key, 'phi^2']
            assert np.isclose(phi_value, value, atol=0.01), \
            f"phi^2 for {key} should be {value}, but got {phi_value}."

        return self # Allow method chaining
    
    # ---- Composite Test Methods ----
    def test_all_anova_components(self):
        """Run all ANOVA component tests in the correct sequence."""
        return (self.test__calculate_t_values()
            .test__calculate_variance()
            .test_calculate_anova())
        
    def test_full_analysis(self):
        """Run all tests including g-coefficients."""
        return self.test_all_anova_components().test__calculate_g_coeffs()
    