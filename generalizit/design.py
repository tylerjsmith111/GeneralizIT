# -------------------------------- #
# Description:
# This is the analytical engine for the Generalizability Theory (G-Theory) calculations.
# It calculates variance components, G-coefficients, and other related statistics.
# -------------------------------- #

import pandas as pd
import numpy as np
from itertools import product, combinations
from scipy.stats import norm
import copy
from typing import Union, Optional
from generalizit.g_theory_utils import create_pseudo_df

class Design:
    def __init__(
            self,
            data: pd.DataFrame,
            variance_tuple_dictionary: dict,
            missing_data: bool = False,
            response_col: str = 'Response'
    ):
        self.data: pd.DataFrame = data
        self.variance_tuple_dictionary: dict = variance_tuple_dictionary
        self.missing_data: bool = missing_data
        self.response_col: str = response_col

        # Initialize the tables
        self.levels_coeffs: pd.DataFrame = pd.DataFrame()
        self.variance_coeffs_table: pd.DataFrame = pd.DataFrame()
        self.anova_table: pd.DataFrame = pd.DataFrame()
        self.g_coeffs_table: pd.DataFrame = pd.DataFrame()
        
        # Initialize the dictionaries
        self.T: dict = {}
        self.variances: dict = {}
        self.d_study_dict: dict  = {}
        self.confidence_intervals: dict = {}
        
        # Initialize alpha for confidence intervals
        self._alpha: float = 0.05

    def _calculate_levels_coeffs(self, **kwargs) -> pd.DataFrame:
        """
        Calculate the levels coefficients for variance components based on grouping combinations.
    
        This method calculates the levels coefficients used to adjust variance components
        in Generalizability Theory. It processes the provided data to compute grouping
        combinations and their respective harmonic means, storing the results in a levels
        coefficients DataFrame.
    
        Parameters:
            **kwargs: Optional keyword arguments.
                - df (pd.DataFrame): A custom DataFrame to use for calculations. If not provided,
                  the default `self.data` is used.
                - variance_tuple_dictionary (dict): Custom variance tuple dictionary.
                  If not provided, self.variance_tuple_dictionary is used.
    
        Returns:
            pd.DataFrame: A DataFrame containing the levels coefficients, where rows and columns
                        correspond to facets. Values represent inverse level coefficients (1/n_i).
    
        Notes:
            - The method automatically identifies the facet with the maximum grouping variables
              and assigns a coefficient of 1 to all entries in its row.
            - The "mean" facet is excluded from calculation.
            - For unbalanced designs, harmonic means are used to calculate appropriate coefficients.
            - Values in the returned DataFrame represent the inverse of the effective sample size (1/n_i).
        """
        # Step 1: Use the provided DataFrame or default to self.data 
        df = kwargs.get('df', self.data)
        variance_tup_dict = kwargs.get('variance_tuple_dictionary', self.variance_tuple_dictionary)
        

        # Step 2: Initialize levels coefficients table with variance components as index and columns
        levels_coeffs = pd.DataFrame(index=variance_tup_dict.keys(),
                                          columns=variance_tup_dict.keys())

        # Drop the "mean" facet from rows and columns
        levels_coeffs.drop('mean', axis=0, errors='ignore', inplace=True)
        levels_coeffs.drop('mean', axis=1, errors='ignore', inplace=True)

        # Step 3: Handle missing data if applicable
        if self.missing_data:
            df = df.dropna()

        # Step 4: Identify the facet with the maximum grouping variables
        max_facet = max(variance_tup_dict, key=lambda x: len(variance_tup_dict[x]))

        # Step 5: Iterate through each variance component to calculate levels coefficients
        for key, differentiation_vars in variance_tup_dict.items():
            if key == 'mean':
                continue

            if key == max_facet:
                levels_coeffs.loc[key] = 1
                continue

            facet_of_differentiation_list = list(differentiation_vars)

            # Iterate through each grouping facet to calculate levels
            for grouping_facet, grouping_vars in variance_tup_dict.items():
                if grouping_facet == 'mean':
                    continue

                grouping_columns = facet_of_differentiation_list + [var for var in grouping_vars if
                                                                    var not in facet_of_differentiation_list]

                # Step 6: Count the occurrences of each grouping combination
                counts_df = df.groupby(grouping_columns).size().reset_index(name='count')

                if facet_of_differentiation_list:
                    # Step 7: Calculate metrics in a single groupby operation
                    grouped = counts_df.groupby(facet_of_differentiation_list).agg({
                        'count': ['sum', lambda x: x.sum() ** 2, lambda x: (x ** 2).sum()]
                    }).reset_index()

                    # Rename columns for clarity
                    grouped.columns = [*facet_of_differentiation_list, 'count', 'sum_squared', 'sum_of_squares']

                    # Step 8: Calculate the ratio of sum_squared to sum_of_squares
                    grouped['ratio'] = grouped['sum_squared'] / grouped['sum_of_squares']

                    # Step 9: Calculate the harmonic mean of the ratio
                    inverse_level = np.mean(1 / grouped['ratio'])
                    level = 1 / inverse_level

                    # Store the calculated level in the levels coefficients table
                    levels_coeffs.at[key, grouping_facet] = inverse_level

        return levels_coeffs

    def _calculate_degrees_of_freedom(self):
        """
        DEPRECATED since v0.1.0: This method is no longer supported.
        
        This method was originally intended to calculate degrees of freedom for variance components
        but is no longer used in the current implementation of G-Theory calculations.
        """
        pass

    def _calculate_T_values(self):
        """
        Calculate the uncorrected sum of squares (T values) for each variance component.

        This method computes the T values for each entry in the variance tuple dictionary by:
        1. For components with effect variables: Groups the data by those variables, 
           calculates the mean and count for each group, and sums the squared means 
           multiplied by their group sizes.
        2. For the mean component (empty effect variables): Calculates the T value 
           using the overall mean and count of the entire dataset.

        The results are stored in the `self.T` dictionary, with keys matching those in 
        `self.variance_tuple_dictionary`.

        Returns:
            None: Updates `self.T` in place with the calculated T values.

        Example:
            If the variance tuple dictionary contains {'p': ('p',), 'i': ('i',), 'mean': ()},
            `self.T` will be populated with T values for 'p', 'i', and 'mean'.
        """
        df = self.data

        for key in self.variance_tuple_dictionary.keys():
            try:
                effect_vars = list(self.variance_tuple_dictionary[key])

                if effect_vars:
                    # Group the DataFrame by the specified effect variables and calculate group mean and size
                    t_calc_df = df.groupby(effect_vars).agg({self.response_col: ['mean', 'count']})

                    # Flatten the MultiIndex columns to single level for easier access
                    t_calc_df.columns = t_calc_df.columns.droplevel()

                    # Reset the index to make grouped columns part of the DataFrame again
                    t_calc_df = t_calc_df.reset_index()

                    # Calculate the T value for each group: (mean^2) * count
                    t_calc_df['t'] = (t_calc_df['mean'] ** 2) * t_calc_df['count']

                    # Return the total uncorrected sum of squares by summing the T values
                    self.T[key] = t_calc_df['t'].sum()

                # Mean calculations if no effect variables are provided
                else:
                    # Calculate the overall mean and count for the entire DataFrame
                    mean = df['Response'].mean()
                    count = df['Response'].count()

                    # Return the T value for the overall mean: (mean^2) * count
                    self.T[key] = (mean ** 2) * count

            except Exception as e:
                raise ValueError(f"Error calculating T values: {e}")

        # Round the T values to 4 decimal places
        self.T = {key: round(value, 4) for key, value in self.T.items()}

    def _calculate_sums_of_squares(self):
        """
        DEPRECATED since v0.1.0: This method is no longer supported.
        
        This method was originally intended to calculate sums of squares for variance components
        but is no longer used in the current implementation of G-Theory calculations.
        """
        pass

    def _calculate_mean_squares(self):
        """
        DEPRECATED since v0.1.0: This method is no longer supported.
        
        This method was originally intended to calculate mean squares for variance components
        but is no longer used in the current implementation of G-Theory calculations.
        """
        pass

    def _calculate_variance_coefficients(
        self,
        df: pd.DataFrame,
        grouping_vars: list,
        facets: list
    ) -> float:
        """
        Calculate the variance or mean coefficient for a dataset based on grouped occurrences.

        This function computes a variance coefficient based on the squared sum of counts
        for each grouping variable, normalized by the total count for each group (or overall,
        if no facets are provided). It generalizes the calculation for both variance coefficients
        (based on grouping facets) and mean coefficients (entire dataset).

        Parameters:
            df (pd.DataFrame): Input dataset containing the relevant variables.
            grouping_vars (list): List of column names used for grouping counts (`variances`).
            facets (list): List of column names defining additional grouping levels (`facets`).
                           If empty, the coefficient is calculated across the entire dataset.

        Returns:
            float: The computed variance or mean coefficient.

        Example:
            # Variance Coefficient
            calculate_variance_coefficient(df, grouping_vars=['i'], facets=['d', 'p'])

            # Mean Coefficient
            calculate_variance_coefficient(df, grouping_vars=['i'], facets=[])
        """
        # Mean facet and mean variance coefficient is the size of the dataset
        if not grouping_vars:
            return len(df)  # No grouping variables: Return the total count of rows

        # Prepare the list of grouping columns
        grouping_columns = facets[:]  # Copy the facets list to avoid modifying the original
        for variance in grouping_vars:
            if variance not in grouping_columns:
                grouping_columns.append(variance)

        # Step 1: Count the occurrences of each grouping combination
        counts_df = df.groupby(grouping_columns).size().reset_index(name='count')

        if facets:
            # Step 2: Sum the total counts for each facet group
            total_counts_df = counts_df.groupby(facets)['count'].sum().reset_index(name='total_count')

            # Step 3: Merge total counts with individual counts
            merged_df = counts_df.merge(total_counts_df, on=facets)

            # Step 4: Calculate the squared count divided by the total count for each group
            merged_df['squared_term'] = (merged_df['count'] ** 2) / merged_df['total_count']

            # Step 5: Sum the squared terms for each facet group and return the overall sum
            result_df = merged_df.groupby(facets)['squared_term'].sum().reset_index()
            return result_df['squared_term'].sum()
        else:
            # Facets are empty: Compute mean coefficient for the entire dataset
            total_count = counts_df['count'].sum()

            counts_df['squared_term'] = (counts_df['count'] ** 2) / total_count

            # Sum the squared terms and return
            return counts_df['squared_term'].sum()

    def _create_variance_coefficients_table(self):
        """
        Create a variance coefficient matrix based on groupings defined in a variance tuple dictionary.

        This function computes variance coefficients for each pair of variance components and
        returns the results in a DataFrame.

        Attributes:
            data (pd.DataFrame): The input DataFrame containing the data to calculate coefficients.
            variance_tuple_dictionary (dict): A dictionary where keys are variance components, and values
                                      are tuples of grouping variables.
            missing_data (bool): Whether to drop rows with NaN values before calculations. Default is True.

        Returns:
            pd.DataFrame: A square DataFrame where the rows and columns represent variance components,
                          and the values represent the calculated variance coefficients.

        Example:
            >>> df = pd.DataFrame({
                    'p': [1, 1, 2, 2],
                    'h': [1, 2, 1, 2],
                    'i': [1, 2, 1, 2],
                    'Response': [0.1, 0.2, 0.3, 0.4]
                })
            >>> variance_tup_dict = {
                    'p': ('p',),
                    'h': ('h',),
                    'i:h': ('i', 'h'),
                    'p x h': ('p', 'h'),
                    'p x (i:h)': ('p', 'i', 'h'),
                    'mean': ()
                }
            >>> self._create_variance_coefficients_table()
                     p      h    i:h  p x h  p x (i:h)  mean
            p        n      ...   ...   ...       ...     n
            h        ...    n     ...   ...       ...     n
            i:h      ...    ...   n     ...       ...     n
            p x h    ...    ...   ...   n         ...     n
            p x (i:h) ...   ...   ...   ...       n       n
            mean     ...    ...   ...   ...       1       n
        """

        # Step 0: Optionally drop rows with NaN values
        if self.missing_data:
            df = self.data.dropna()
        else:
            df = self.data

        # Initialize the square DataFrame with variance components as both rows and columns
        variance_components = list(self.variance_tuple_dictionary.keys())
        self.variance_coeffs_table = pd.DataFrame(
            index=variance_components, columns=variance_components, dtype=np.float64
        )

        # Step 1: Compute variance coefficients for each pair of variance components
        for row_facet in variance_components:
            for col_variance in variance_components:
                grouping_vars = list(self.variance_tuple_dictionary[col_variance])
                facets = list(self.variance_tuple_dictionary[row_facet])
                self.variance_coeffs_table.at[row_facet, col_variance] = self._calculate_variance_coefficients(
                    df=df,
                    grouping_vars=grouping_vars,
                    facets=facets
                )

        # Check that the dtype is float64
        self.variance_coeffs_table = self.variance_coeffs_table.astype(np.float64)

        # Round the values to 4 decimal places
        self.variance_coeffs_table = self.variance_coeffs_table.round(4)

    def _create_regression_matrix(self) -> pd.DataFrame:
        """
        Create a regression matrix for variance component estimation.

        This method constructs a regression matrix by combining variance coefficients
        with their corresponding T values. The resulting matrix is used for solving the
        system of equations to estimate variance components.

        Returns:
            pd.DataFrame: A DataFrame containing the regression matrix, where rows correspond
                          to facets and columns represent variance coefficients and T values.

        Example:
            Index: ['facet1', 'facet2']
            Columns: ['Variance1', 'Variance2', ..., 'T']
        """
        # Create a copy of the variance coefficients table
        regression_df = self.variance_coeffs_table.copy()

        # Add a column for T values using the T dictionary
        regression_df['T'] = [self.T[facet] for facet in regression_df.index]

        return regression_df

    def _calculate_variance(self):
        """
        Calculate variance components using a regression matrix.

        This method solves a linear system of equations where the regression matrix
        represents the coefficients of variance components and the right-hand side
        vector corresponds to the T values. The solution gives the variance components,
        which are stored in the ANOVA table.

        Steps:
            1. Construct the regression matrix using `_create_regression_matrix`.
            2. Solve the linear system using `np.linalg.solve`.
            3. Store the calculated variance components in the ANOVA table.
        """
        # Step 1: Create the regression matrix
        df = self._create_regression_matrix()

        # Step 2: Extract the coefficient matrix (A) and right-hand side vector (B)
        A = df.drop('T', axis=1).values.astype(np.float64)  # Coefficient matrix
        B = df['T'].values.astype(np.float64)  # Right-hand side vector

        # Step 3: Solve the system of linear equations
        X = np.linalg.solve(A, B)  # Variance components

        # Step 4: Round the solution for clarity
        X = np.round(X, 4)

        # Step 5: Update the DataFrame with calculated variances
        df['T'] = B
        df['Variance'] = X

        # Step 6: Store the ANOVA table for future use
        self.anova_table = df.copy()

    def calculate_anova(self):
        """
        Performs analogous ANOVA calculations using Henderson 1953 Method 1.
        Determines the variance components from variance coefficients and
        uncorrected sum of squares (T values) for each facet, iteractions, and means.

        This method executes the steps necessary to estimate variance components based
        on Generalizability Theory. This method does not require corrected Sum of Squares or Mean Squares,
        and thus they are not calculated. It also does not calculate hypothesis tests or F-statistics,
        as these are not relevant in G-Theory.

        Steps:
            1. Calculate the T values using `_calculate_T_values`.
            2. Create the variance coefficients table with `_create_variance_coefficients_table`.
            3. Estimate variance components using `_calculate_variance`.

        Note:
            - This method does not require and does not calculate Sum of Squares or Mean Squares.
            - This method emphasizes variance component estimation over hypothesis testing.

        """
        # Step 1: Calculate the T values
        self._calculate_T_values()

        # Step 2: Create the variance coefficients table
        self._create_variance_coefficients_table()

        # Step 3: Estimate the variance components
        self._calculate_variance()

    def _get_tau_facets(
            self,
            facet_of_differentiation: str,
            facet_of_differentiation_tup: tuple,
            variance_tup_dict: dict,
    ) -> list:
        """
        Determine the appropriate facets to include in the tau calculation for generalizability coefficients.

        This function identifies the primary facet of differentiation and any lower-order interaction facets
        that are subsets of the current facet tuple (`facet_of_differentiation_tup`) and exist in the
        `variance_tup_dict`. The resulting list is used in calculations for generalizability coefficients.

        Parameters:
            facet_of_differentiation (str): The primary facet for which tau is being calculated.
            facet_of_differentiation_tup (tuple): Tuple representing the facet's structure (e.g., nested or crossed facets).
            variance_tup_dict (dict): Dictionary where keys are facet names and values are tuples representing
                                      the structure of their variance components.

        Returns:
            list: A list of facets to include in the tau calculation. Includes the primary facet and any valid
                  lower-order interaction facets.

        Example:
            >>> variance_tup_dict = {'p': ('p',), 'pi': ('p', 'i'), 'mean': ()}
            >>> self._get_tau_facets(df, 'pi', ('p', 'i'), variance_tup_dict)
            ['pi', 'p']
        """
        # Initialize the tau facets with the primary facet of differentiation
        tau_facets = [facet_of_differentiation]

        # Check for interactions if the facet tuple has more than one element
        if len(facet_of_differentiation_tup) > 1:
            # Generate all potential lower-order subsets of the facet tuple
            for i in range(len(facet_of_differentiation_tup) - 1, 0, -1):
                # Generate all combinations of the tuple elements of length i
                combos = {frozenset(combo) for combo in combinations(facet_of_differentiation_tup, i)}

                # Check if these combinations exist in the variance dictionary
                for key, variance_tup in variance_tup_dict.items():
                    if len(variance_tup) == i and frozenset(variance_tup) in combos:
                        tau_facets.append(key)

        return tau_facets

    def _calculate_tau(
            self,
            df: pd.DataFrame,
            tau_facets: list,
    ) -> float:

        tau = df.loc[tau_facets, 'Variance'].sum()

        return tau

    def _get_big_delta_facets(
            self,
            tau_facets: list,
            variance_tup_dict: dict,
    ) -> list:

        # Any variance component not in the tau facets is part of the Delta (Δ) calculation
        return [key for key in variance_tup_dict.keys() if key not in tau_facets]

    def _calculate_big_delta(
            self,
            df: pd.DataFrame,
            facet_of_differentiation: str,
            big_delta_facets: list,
            levels_df: pd.DataFrame,
    ) -> float:

        Delta = 0

        # for facet in variance_tup_dict.keys():
        for facet in big_delta_facets:
            variance = df.loc[facet, 'Variance']

            Delta += variance * levels_df.loc[
                facet_of_differentiation, facet]  # levels_df returns 1 / level so variance * levels_df is equivalent to variance / alpha

        return Delta


    def _calculate_phi_squared(
            self,
            df: pd.DataFrame,
            facet_of_differentiation: str,
            variance_tup_dict: dict,
            levels_df: pd.DataFrame
    ) -> float:
        """
        Calculate the phi-squared (φ²) coefficient for a given facet of differentiation.

        The phi-squared coefficient quantifies the proportion of total variance attributable
        to the specified facet of differentiation. It is calculated using the variance components
        and levels from the provided dictionaries.

        Parameters:
            df (pd.DataFrame): A DataFrame containing variance components with a 'Variance' column.
                               It should include rows and columns corresponding to facets of differentiation.
            facet_of_differentiation (str): The facet for which φ² is being calculated.
            variance_tup_dict (dict): A dictionary where keys are facet names and values are tuples
                                      representing the facets that contribute to the variance.
            levels_df (pd.DataFrame): A DataFrame where keys are facet names and values are their respective
                                levels coefficient (1 / levels).

        Returns:
            float: The calculated φ² coefficient for the specified facet of differentiation.

        Example:
            >>> df = pd.DataFrame({'Variance': [1.0, 0.5, 0.2]}, index=['p', 'i', 'mean'])
            >>> variance_tup_dict = {'p': ('p',), 'i': ('i',), 'mean': ()}
            >>> levels_df = pd.DataFrame({'p': [0.5, 0.2, 1.0], 'i': [0.2, 0.5, 1.0], 'mean': [1.0, 1.0, 1.0]})
            >>> self._calculate_phi_squared(df, 'p', variance_tup_dict, levels_dict)
            0.8333
        """
        print(f"Facet of Differentiation: {facet_of_differentiation}")

        # Step 1: Extract the tuple for the facet of differentiation
        facet_of_differentiation_tup = variance_tup_dict[facet_of_differentiation]

        # Step 2: Extract the variance (τ) for the facet of differentiation
        tau_facets = self._get_tau_facets(
            facet_of_differentiation=facet_of_differentiation,
            facet_of_differentiation_tup=facet_of_differentiation_tup,
            variance_tup_dict=variance_tup_dict
        )

        tau = self._calculate_tau(df, tau_facets)

        print(f"Tau (τ) facets: {tau_facets}")
        print(f"Tau (τ): {tau}")

        # Step 3: Initialize the Delta List (error variances) and calculate the Delta (Δ) value
        Delta_facets = self._get_big_delta_facets(
            tau_facets=tau_facets,
            variance_tup_dict=variance_tup_dict
        )

        print(f"Delta (Δ) facets: {Delta_facets}")

        Delta = self._calculate_big_delta(
            df=df,
            facet_of_differentiation=facet_of_differentiation,
            big_delta_facets=Delta_facets,
            levels_df=levels_df
        )

        print(f"Delta (Δ): {Delta}")

        # Step 4: Calculate φ² using the tau and Delta values
        phi_squared = tau / (tau + Delta)

        # # Debugging logs (optional, can be removed in production)
        # print(f"Tau (τ): {tau}")
        # print(f"Delta (Δ): {Delta}")

        return phi_squared

    def _get_little_delta_facets(
            self,
            tau_facets: list,
            facet_of_differentiation: str,
            facet_of_differentiation_tup: tuple,
            variance_tup_dict: dict,
    ) -> list:

        # Initialize the delta facets
        little_delta_facets = []

        for facet, tup in variance_tup_dict.items():
            # Skip entries that don't contribute to delta calculation:
            # 1. Mean facet
            # 2. Facet of differentiation itself
            # 3. Facets with fewer elements than facet of differentiation
            # 4. Facets already included in tau calculation
            if (facet == 'mean' or
                    facet == facet_of_differentiation or
                    len(tup) < len(facet_of_differentiation_tup) or
                    facet in tau_facets):
                continue

            print(f"delta (δ) Facet: {facet}, Tuple: {tup}")

            # Check if any elements of the differentiation tuple are in the current tuple
            if any(f in tup for f in facet_of_differentiation_tup):
                little_delta_facets.append(facet)

        return little_delta_facets

    def _calculate_little_delta(
            self,
            df: pd.DataFrame,
            facet_of_differentiation: str,
            little_delta_facets: list,
            levels_df: pd.DataFrame
    ) -> float:

        delta = 0

        # for facet in variance_tup_dict.keys():
        for facet in little_delta_facets:
            variance = df.loc[facet, 'Variance']

            delta += variance * levels_df.loc[
                facet_of_differentiation, facet]  # levels_df returns 1 / level so variance * levels_df is equivalent to variance / alpha_star

        return delta

    def _calculate_rho_squared(
            self,
            df: pd.DataFrame,
            facet_of_differentiation: str,
            variance_tup_dict: dict,
            levels_df: pd.DataFrame,
    ) -> float:
        """
            Calculate the rho-squared (ρ²) coefficient for a given facet of differentiation.

            The rho-squared coefficient measures the proportion of total variance attributable to
            the specified facet of differentiation, considering only facets nested within the
            differentiation tuple.

            Parameters:
                df (pd.DataFrame): A DataFrame containing variance components with a 'Variance' column.
                                   It should include rows and columns corresponding to facets of differentiation.
                facet_of_differentiation (str): The facet for which ρ² is being calculated.
                variance_tup_dict (dict): A dictionary where keys are facet names and values are tuples
                                          representing the facets that contribute to the variance.
                levels_df (pd.DataFrame): A DataFrame where indices are facet names and values are their respective
                                    levels coefficient (1 / levels).

            Returns:
                float: The calculated ρ² coefficient for the specified facet of differentiation.

            Example:
                >>> df = pd.DataFrame({'Variance': [1.0, 0.5, 0.2]}, index=['p', 'i', 'mean'])
                >>> variance_tup_dict = {'p': ('p',), 'i': ('p', 'i'), 'mean': ()}
                >>> levels_dict = pd.DataFrame({'p': [0.5, 0.2, 1.0], 'i': [0.2, 0.5, 1.0], 'mean': [1.0, 1.0, 1.0]})
                >>> self._calculate_rho_squared(df, 'p', variance_tup_dict, levels_dict)
                0.8333
            """
        print(f"ρ² Facet of Differentiation: {facet_of_differentiation}")

        # Step 1: Extract the tuple for the facet of differentiation
        facet_of_differentiation_tup = variance_tup_dict[facet_of_differentiation]

        # Step 2: Extract the variance (τ) for the facet of differentiation and any lower interaction facets within the tuple
        tau_facets = self._get_tau_facets(
            facet_of_differentiation=facet_of_differentiation,
            facet_of_differentiation_tup=facet_of_differentiation_tup,
            variance_tup_dict=variance_tup_dict
        )

        tau = self._calculate_tau(df, tau_facets)

        print(f"Tau Facets: {tau_facets}")
        print(f"Tau (τ): {tau}")

        # Step 3: Get the facets for the delta calculation
        little_delta_facets = self._get_little_delta_facets(
            tau_facets=tau_facets,
            facet_of_differentiation=facet_of_differentiation,
            facet_of_differentiation_tup=facet_of_differentiation_tup,
            variance_tup_dict=variance_tup_dict
        )

        # Step 4: Calculate delta (δ) using the variance components and levels_df
        delta = self._calculate_little_delta(
            df=df,
            facet_of_differentiation=facet_of_differentiation,
            little_delta_facets=little_delta_facets,
            levels_df=levels_df
        )

        # print(f"Delta Facets: {delta_facets}")
        print(f"Delta (δ): {delta}")

        # Step 4: Calculate ρ² using tau and delta values
        rho_squared = tau / (tau + delta)

        # # Debugging logs (optional, can be removed in production)
        # print(f"Tau (τ): {tau}")
        # print(f"delta (δ): {delta}")

        return rho_squared


    def _calculate_g_coeffs(self, variance_df: pd.DataFrame, levels_df: pd.DataFrame, variance_tup_dict: dict) -> pd.DataFrame:
        """
        Calculate the G-coefficients for each facet of differentiation.
        """
        # Step 1: Initialize the G coefficients DataFrame
        columns = list(variance_df.columns) + ['phi^2', 'rho^2']
        g_coeffs_df = variance_df.copy()
        g_coeffs_df = g_coeffs_df.reindex(columns=columns)

        # Step 2: Calculate the G coefficients for each facet up until the largest facet
        largest_facet = max(variance_tup_dict, key=lambda x: len(variance_tup_dict[x]))
        for facet in variance_df.index:
            if facet == 'mean' or facet == largest_facet:
                continue

            # Calculate the phi-squared coefficient
            g_coeffs_df.at[facet, 'phi^2'] = self._calculate_phi_squared(variance_df, facet_of_differentiation=facet,
                                                                   variance_tup_dict=variance_tup_dict,
                                                                   levels_df=levels_df)

            # Calculate the rho-squared coefficient
            g_coeffs_df.at[facet, 'rho^2'] = self._calculate_rho_squared(variance_df, facet_of_differentiation=facet,
                                                                   variance_tup_dict=variance_tup_dict,
                                                                   levels_df=levels_df)

        # Drop any columns that are not 'phi^2' or 'rho^2'
        g_coeffs_df = g_coeffs_df[['phi^2', 'rho^2']]

        # Drop any rows with NaN values
        g_coeffs_df.dropna(inplace=True)

        # Round the values to 4 decimal places
        g_coeffs_df = g_coeffs_df.round(4)

        return g_coeffs_df

    def g_coeffs(self, **kwargs):
        """
        Calculate G-coefficients for various scenarios of fixed and random facets.
        
        This method computes rho^2 (relative) and phi^2 (absolute) coefficients for each 
        potential object of measurement in the design. The coefficients quantify the 
        reliability of measurements across different facets.
        
        Parameters:
            **kwargs: Optional keyword arguments.
                - variance_dictionary (dict): Custom variance components to use.
                    If provided, values must be non-negative. If not provided, 
                    components from the ANOVA table are used.
                - levels_df (pd.DataFrame): Custom levels coefficients table.
                    If not provided, self.levels_coeffs is used or calculated.
                - variance_tuple_dictionary (dict): Custom variance tuple dictionary.
                    If not provided, self.variance_tuple_dictionary is used.
                - d_study (bool): If True, returns the G-coefficients DataFrame directly
                    instead of storing it in self.g_coeffs_table. Default is False.
        
        Returns:
            pd.DataFrame or None: If d_study=True, returns the G-coefficients DataFrame directly.
            Otherwise, results are stored in self.g_coeffs_table and None is returned.
            
        Raises:
            ValueError: If:
                - ANOVA table hasn't been calculated and no variance_dictionary is provided
                - Any variance component is negative
                - Levels coefficients are invalid (non-square, negative values)
                - Keys in variance_dictionary don't match variance_tuple_dictionary
                - Levels coefficients don't match variance components
        
        Notes:
            - Negative variance components are automatically set to zero with a warning
            - The 'mean' component is removed from calculations
            - The method produces a DataFrame with rho^2 and phi^2 values for each facet
        """
        # Set the variance tuple dictionary (in case the design has been updated)
        if 'variance_tuple_dictionary' in kwargs:
            variance_tup_dict = kwargs['variance_tuple_dictionary']
            if not isinstance(variance_tup_dict, dict):
                raise ValueError("Variance tuple dictionary must be a dictionary.")
            for value in variance_tup_dict.values():
                if not isinstance(value, tuple):
                    raise ValueError(
                        f"Variance tuple dictionary component '{key}' is not a tuple.")
            print("Using user-provided variance tuple dictionary")
        else:
            # Use the default variance tuple dictionary
            print("Using default variance tuple dictionary")
            variance_tup_dict = self.variance_tuple_dictionary
            
        variance_tup_dict.pop('mean', None)
        
        # Process the variance dictionary
        if 'variance_dictionary' in kwargs:
            variance_dict = kwargs['variance_dictionary']
            if not isinstance(variance_dict, dict):
                raise ValueError("Variance dictionary must be a dictionary.")
            
            print("Using user-provided variance dictionary")
            
            # Validate the variance dictionary
            for key, value in variance_dict.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Variance component '{key}' is not a number.")
                if value < 0:
                    raise ValueError(
                        f"Variance component '{key}' is negative.")
            if set(variance_dict.keys()) != set(variance_tup_dict.keys()):
                raise ValueError(
                    f"Variance dictionary keys do not match the variance tuple dictionary keys. Mismatched keys: {variance_dict.keys()} and {variance_tup_dict.keys()}")
            
            # Convert to DataFrame to match anova_table structure
            variance_df = pd.DataFrame({'Variance': variance_dict})
        else:
            # Check if the ANOVA table has been calculated
            if self.anova_table.empty:
                raise ValueError("Please calculate the ANOVA table using the calculate_anova method before calculating the confidence intervals.")
            print("Using ANOVA Table Variance Dictionary for Generalizability Coefficients")
            variance_df = self.anova_table.copy()
            
        
        # Process the variance dictionary
        variance_df = variance_df.drop('mean', axis=0, errors='ignore')
        variance_df = variance_df.drop('mean', axis=1, errors='ignore')
        if (variance_df['Variance'] < 0).any():
            # Print a warning message and set negative values to 0
            print(f"Warning: Negative variance components found for {variance_df[variance_df['Variance'] < 0].index}. Setting to 0.")
            variance_df.loc[variance_df['Variance'] < 0, 'Variance'] = 0
        # Check that variance DataFrame indices match the variance tuple dictionary keys
        if set(variance_df.index) != set(variance_tup_dict.keys()):
            raise ValueError(f"ANOVA table indices do not match the variance tuple dictionary keys. Mismatched indices: {self.anova_table.index.tolist()} and {variance_tup_dict.keys()}")
                    
        # Check if the levels coefficients have been calculated
        if 'levels_df' in kwargs:
            levels_df = kwargs['levels_df']
            if not isinstance(levels_df, pd.DataFrame):
                raise ValueError("Levels coefficients must be a DataFrame.")
            print("Using User Provided Levels Coefficients")
            if set(levels_df.index) != set(variance_df.index):
                raise ValueError(f"Levels coefficients must match the variance components. Mismatched indices: {levels_df.index.tolist()} and {list(variance_dict.keys())}")
            if set(levels_df.columns) != set(levels_df.index):
                raise ValueError(f"Levels coefficients must have a square shape with a value for each facet. Mismatched columns: {levels_df.columns.tolist()} and {levels_df.index.tolist()}")
            if levels_df.values.min() <= 0:
                raise ValueError(f"Levels coefficients must be greater than 0. Minimum value: {levels_df.values.min()}")
        elif not self.levels_coeffs.empty:
            # check that the levels coefficient indices match the variance components
            if set(self.levels_coeffs.index) != set(variance_df.index):
                raise ValueError(f"Levels coefficients must match the variance components. Mismatched indices: {self.levels_coeffs.index.tolist()} and {variance_df.index.tolist()}")
            
            levels_df = self.levels_coeffs
        else:
            self.levels_coeffs = self._calculate_levels_coeffs() # Calculate the levels coefficients
            
            if set(self.levels_coeffs.index) != set(variance_df.index):
                raise ValueError(f"Levels coefficients must match the variance components. Mismatched indices: {self.levels_coeffs.index.tolist()} and {variance_df.index.tolist()}")
            
            levels_df = self.levels_coeffs

        # Store the G-coefficients in a table
        d_study = kwargs.get('d_study', False)  # Default to False if not provided

        if not isinstance(d_study, bool):
            raise ValueError("d_study must be a boolean value.")

        # Calculate G-coefficients
        result = self._calculate_g_coeffs(variance_df=variance_df, levels_df=levels_df, variance_tup_dict=variance_tup_dict)

        # Either return the result (in the case of a D-Study) or store it in the class attribute to maintain compatibility
        if d_study:
            return result
        else:
            self.g_coeffs_table = result
        
    # ----------------- D STUDY -----------------
    def _process_d_study_helper(
        self, 
        pseudo_counts_df: pd.DataFrame, 
        variance_tuple_dictionary: dict, 
        variance_dictionary: Optional[dict] =None, 
        scenario_label: Optional[str] =None,
        ) -> None:
        """
        Helper method to process a single D-Study scenario and append it to the d_study_dict attribute.
        
        Parameters:
            pseudo_counts_df (pd.DataFrame): The pseudo counts DataFrame for this scenario
            variance_tuple_dictionary (dict): Dictionary mapping components to facet tuples
            variance_dictionary (dict, optional): Custom variance components to use
            scenario_label (str, optional): Label for this scenario. If None, generated from pseudo_counts_df
            
        Returns:
            None: Results are appended to self.d_study_dict with the scenario label as key
        """
        # Create the pseudo levels df
        pseudo_levels_df = self._calculate_levels_coeffs(
            df=pseudo_counts_df,
            variance_tuple_dictionary=variance_tuple_dictionary
        )
        
        # Prepare kwargs for g_coeffs
        g_coeffs_kwargs = {
            'levels_df': pseudo_levels_df,
            'variance_tuple_dictionary': variance_tuple_dictionary,
            'd_study': True,
        }
        
        # Add variance_dictionary if provided
        if variance_dictionary is not None:
            g_coeffs_kwargs['variance_dictionary'] = variance_dictionary
            
        # Get G-coefficients table
        pseudo_g_coeffs_table = self.g_coeffs(**g_coeffs_kwargs)
        
        # Create a label if not provided
        if scenario_label is None:
            scenario_label = ', '.join([f"{key}: {value}" for key, value in pseudo_counts_df.items()])
        
        # Add to d_study_dict
        self.d_study_dict[scenario_label] = pseudo_g_coeffs_table
    
    
    def calculate_d_study(self, d_study_design: Union[dict, None], **kwargs):
        """
        Implement a D-Study to determine optimal facet levels based on G-Study variance components.
        
        This method examines multiple possible study designs by generating all combinations
        of the provided facet levels. It calculates G-coefficients for each design scenario
        using the variance components from a previously conducted G-Study.
        
        Parameters:
            d_study_design (dict): Dictionary where keys are facet names and values are 
                lists of integers representing different numbers of levels to test.
                For example:
                {
                    'person': [10],        # Only testing 10 persons
                    'item': [2, 3],        # Testing either 2 or 3 items
                    'rater': [2, 4, 6]     # Testing 2, 4, or 6 raters
                }
                This would generate 6 different study designs (1×2×3 combinations).
                        
            **kwargs: Optional additional parameters.
        
        Returns:
            None: Results are stored in self.d_study_dict, where keys are string
            representations of each design scenario and values are DataFrames
            containing the corresponding G-coefficients.
            
        Raises:
            ValueError: If d_study_design is not properly formatted or if required
            precalculations haven't been performed.
            
        Notes:
            - This method requires that variance components have been calculated via a G-Study
            - For each design scenario, new levels coefficients are calculated
            - All facet combinations in the original design must be maintained
        """
        
        # Check if a d_study_design dictionary is provided
        if d_study_design is not None:
            print("Performing Balanced D-Study Design for the provided designs")
            if kwargs.get('pseudo_counts_dfs', None) is not None:
                raise ValueError("D-Study design must be provided as a dictionary OR pseudo_counts_dfs: list[pd.DataFrame] must be provided.")
    
            if not isinstance(d_study_design, dict):
                raise ValueError("D-Study design must be a dictionary.")
            # Check that each key in d_study_design appears in at least one tuple in variance_tuple_dictionary
            all_facets_in_variance_tuples = set()
            for component, variance_tuple in self.variance_tuple_dictionary.items():
                if component != 'mean':  # Skip the 'mean' component which typically has an empty tuple
                    all_facets_in_variance_tuples.update(variance_tuple)
                
            unknown_facets = set(d_study_design.keys()) - all_facets_in_variance_tuples
            if unknown_facets:
                raise ValueError(f"Facets {unknown_facets} in d_study_design are not found in any variance component tuple. Valid facets are: {all_facets_in_variance_tuples}")
            # Check that the values are lists of integers
            for key, value in d_study_design.items():
                if not isinstance(value, list):
                    raise ValueError(f"Levels for facet {key} must be a list of integers.")
                if any([not isinstance(val, int) for val in value]):
                    raise ValueError(f"All levels for facet {key} must be integers.")
                if any([val <= 0 for val in value]):
                    raise ValueError(f"All levels for facet {key} must be greater than 0.")
                
            # iterate through potential study designs
            study_designs = []
            
            # Get all possible combinations of levels using itertools.product
            facets = list(d_study_design.keys())
            level_lists = [d_study_design[facet] for facet in facets]
            
            # Generate all combinations using itertools.product
            for combo in product(*level_lists):
                # Create a dictionary for this specific design scenario
                design_scenario = {facet: level for facet, level in zip(facets, combo)}
                study_designs.append(design_scenario)
            
            for study_design in study_designs:
                # create a label by turning the study_design dictionary into a string
                label = ', '.join([f"{key}: {value}" for key, value in study_design.items()])
                
                # Create the pseudo count df
                # Use the variance tuple dictionary from the G study's design
                pseudo_counts_df = create_pseudo_df(d_study=study_design, variance_tup_dict=self.variance_tuple_dictionary)
                                
                # Use the helper function to process the D-Study scenario
                # and add to the d_study_dict
                self._process_d_study_helper(
                    pseudo_counts_df=pseudo_counts_df,
                    variance_tuple_dictionary=self.variance_tuple_dictionary,
                    scenario_label=label,
                )
            
        else:
            # Unbalanced or missing D Study Designs must input manual pseudo counts
            print("Performing Advanced D-Study Design for the provided designs")
            pseudo_counts_dfs = kwargs.get('pseudo_counts_dfs', None)
            if pseudo_counts_dfs is None:
                raise ValueError("D-Study design must be provided as a dictionary or pseudo_counts_dfs: list[pd.DataFrame] must be provided.")
            if not isinstance(pseudo_counts_dfs, list):
                raise ValueError("pseudo_counts_dfs must be a list of DataFrames.")
            if any([not isinstance(df, pd.DataFrame) for df in pseudo_counts_dfs]):
                raise ValueError("All elements in pseudo_counts_dfs must be DataFrames.")
            if any([df.empty for df in pseudo_counts_dfs]):
                raise ValueError("All DataFrames in pseudo_counts_dfs must be non-empty.")
                
            
            if kwargs.get('variance_tuple_dictionary', None) is not None:
                variance_tuple_dictionary = kwargs['variance_tuple_dictionary']
                if not isinstance(variance_tuple_dictionary, dict):
                    raise ValueError("variance_tuple_dictionary must be a dictionary.")
                for value in variance_tuple_dictionary.values():
                    if not isinstance(value, tuple):
                        raise ValueError(
                            f"Variance tuple dictionary component '{key}' is not a tuple.")
                print("Using user-provided variance tuple dictionary")
            else:
                # Use the default variance tuple dictionary
                print("Using default variance tuple dictionary")
                variance_tuple_dictionary = self.variance_tuple_dictionary
                
            # validate that the columns (facets) of the pseudo_counts_dfs can be found in the variance_tuple_dictionary tuples
            all_facets_in_variance_tuples = set()
            for component, variance_tuple in variance_tuple_dictionary.items():
                if component != 'mean':
                    all_facets_in_variance_tuples.update(variance_tuple)
            for df in pseudo_counts_dfs:
                if not set(df.columns).issubset(all_facets_in_variance_tuples):
                    raise ValueError(f"DataFrame columns {df.columns} are not found in any variance component tuple. Valid facets are: {all_facets_in_variance_tuples}")
            
            # check for the variance dictionary
            if kwargs.get('variance_dictionary', None) is not None:
                variance_dictionary = kwargs['variance_dictionary']
                if not isinstance(variance_dictionary, dict):
                    raise ValueError("variance_dictionary must be a dictionary.")
                for key, value in variance_dictionary.items():
                    if not isinstance(value, (int, float)):
                        raise ValueError(
                            f"Variance component '{key}' is not a number.")
                    if value < 0:
                        raise ValueError(
                            f"Variance component '{key}' is negative.")
            else:
                variance_dictionary = {idx: row['Variance'] for idx, row in self.anova_table.iterrows() if idx != 'mean'} # Exclude the mean row
            
            if set(variance_dictionary.keys()) != set(variance_tuple_dictionary.keys()):
                raise ValueError(
                    f"Variance dictionary keys do not match the variance tuple dictionary keys. Mismatched keys: {variance_dictionary.keys()} and {variance_tuple_dictionary.keys()}")
            
            # Enter the D-Study Loop
            for pseudo_counts_df in pseudo_counts_dfs:
                # create a label by turning the study_design dictionary into a string
                label = ', '.join([f"{key}: {value}" for key, value in pseudo_counts_df.items()])
                
                # Use the helper function to process the D-Study scenario
                # and add to the d_study_dict
                self._process_d_study_helper(
                    pseudo_counts_df=pseudo_counts_df,
                    variance_tuple_dictionary=variance_tuple_dictionary,
                    variance_dictionary=variance_dictionary,
                    scenario_label=label,
                )
        
    # ----------------- Confidence Intervals -----------------
    def calculate_confidence_intervals(self, alpha: float=0.05, **kwargs):
        """
        Calculate confidence intervals for means of each facet level.
        
        This method computes confidence intervals for individual facets based on 
        variance component analysis using the formula from Cardinet et al. (1976):
        
        X ± z_(α/2) × √(σ²)
        
        where σ² represents the sum of variance components adjusted by the 
        appropriate levels coefficients.
        
        Parameters:
            alpha (float, optional): Significance level for confidence intervals.
                Default is 0.05 (producing 95% confidence intervals).
            **kwargs: Optional keyword arguments.
                - variance_dictionary (dict): Custom variance components to use.
                If not provided, components from the ANOVA table are used.
                - levels_df (pd.DataFrame): Custom levels coefficients table. 
                If not provided, self.levels_coeffs is used or calculated.
        
        Returns:
            None: Results are stored in self.confidence_intervals
            
        Attributes:
            self.confidence_intervals (dict): Dictionary where keys are facet names and
                values are DataFrames containing confidence intervals for each level.
                Each DataFrame contains columns:
                - lower_bound: Lower CI boundary
                - mean: Observed mean
                - upper_bound: Upper CI boundary
                
        Notes:
            - Confidence intervals are not calculated for the facet with the largest
            dimensionality (typically the interaction term containing all facets).
            - Negative variance components are automatically set to zero with a warning.
            - The method requires the ANOVA table to be calculated first unless
            a custom variance_dictionary is provided.
        
        Raises:
            ValueError: If alpha is not between 0 and 1, ANOVA hasn't been calculated,
                or if invalid parameters are provided.
        """
        # Check if the alpha value is between 0 and 1
        if not (0 < alpha < 1):
            raise ValueError("Alpha must be between 0 and 1.")
        # Check if the alpha value is a number
        if not isinstance(alpha, (int, float)):
            raise ValueError("Alpha must be a number.")
        
        self._alpha = alpha
        
        # add the variance components to a dictionary
        if 'variance_dictionary' in kwargs:
            variance_dict = kwargs['variance_dictionary']
            if not isinstance(variance_dict, dict):
                raise ValueError("Variance dictionary must be a dictionary.")
            print("Using User Provided Variance Dictionary")
            for key, value in variance_dict.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(
                        f"Variance component '{key}' is not a number. Please check the variance dictionary and try again.")
                if value < 0:
                    raise ValueError(
                        f"Variance component '{key}' is negative. Please check the variance dictionary and try again.")
                if key not in self.anova_table.index.to_list():
                    raise ValueError(
                        f"Variance component '{key}' not found in the source of variance. Please check the variance dictionary and try again.")
                
            # variance_dict = {re.sub(r"\s+", " ", key.strip().lower()): value for key, value in variance_dict.items()}
        else:
            # Check if the ANOVA table has been calculated
            if self.anova_table.empty:
                raise ValueError("Please calculate the ANOVA table using the calculate_anova method before calculating the confidence intervals.")
            print("Using ANOVA Table Variance Dictionary")
            variance_dict = {idx: row['Variance'] for idx, row in self.anova_table.iterrows() if idx != 'mean'} # Exclude the mean row
            # Check if any variance components are less than 0
            negative_keys = [key for key, value in variance_dict.items() if value < 0]
            if negative_keys:
                # Print a warning message and set negative values to 0
                print(f"Warning: Negative variance components found for {negative_keys}. Setting to 0.")
                for key in negative_keys:
                    variance_dict[key] = 0
                    
        # Check if the levels coefficients have been calculated
        if 'levels_df' in kwargs:
            print("Using User Provided Levels Coefficients")
            levels_df = kwargs['levels_df']
            if not isinstance(levels_df, pd.DataFrame):
                raise ValueError("Levels coefficients must be a DataFrame.")
            if set(levels_df.columns) != set(levels_df.index):
                raise ValueError(f"Levels coefficients must have a square shape with a value for each facet. Mismatched columns: {levels_df.columns.tolist()} and {levels_df.index.tolist()}")
            if levels_df.values.min() <= 0:
                raise ValueError(f"Levels coefficients must be greater than 0. Minimum value: {levels_df.values.min()}")
        elif not self.levels_coeffs.empty:
            print("Using previously calculated levels coefficients")
            levels_df = self.levels_coeffs
        else:
            print("Calculating levels coefficients")
            self.levels_coeffs = self._calculate_levels_coeffs() # Calculate the levels coefficients
            levels_df = self.levels_coeffs
            
        # Check that the levels coefficients match the variance components
        if set(levels_df.index) != set(variance_dict.keys()):
                raise ValueError(f"Levels coefficients must match the variance components. Mismatched indices: {levels_df.index.tolist()} and {list(variance_dict.keys())}")
           
        self.confidence_intervals = {key: pd.DataFrame() for key in variance_dict.keys()}  # Create a dictionary with empty DataFrames as values

        # Remove the largest facet from the confidence intervals i.e. p x (i:h) since
        # there will be a single value for each unique combination of the other facets
        max_facet = max(self.confidence_intervals, key=lambda x: len(self.variance_tuple_dictionary[x]))
        self.confidence_intervals = {key: self.confidence_intervals[key] for key in self.confidence_intervals if key != max_facet}
        
        for key in self.confidence_intervals:
            
            # Sum the variances all other variances divided by the product of the levels of the other facets
            # Do not include the variance of the facet in question or the level of the facet in question
            # For example, sigma^2(aBC) = sigma^2(b)/n_b + sigma^2(c)/n_c + sigma^2(bc)/n_b*n_c + sigma^2(ab)/n_b + sigma^2(ac)/n_c + sigma^2(abc)/n_b*n_c
            sigma_squared = 0
            
            for var in variance_dict.keys():
                if var == key:
                    continue
                
                sigma_squared += variance_dict[var] * levels_df.loc[key, var]  # levels_df returns 1 / level so variance * levels_df is equivalent to variance / levels
            
            # Use the alpha value to get the z_alpha/2 value
            z_alpha = norm.ppf(1 - self._alpha/2)
            interval = z_alpha * np.sqrt(sigma_squared)

            # First, get just the mean in a clean way
            ci_df = self.data.groupby(list(self.variance_tuple_dictionary[key])).agg({
                self.response_col: 'mean'
            })

            # Rename the column to be clearer
            ci_df = ci_df.rename(columns={self.response_col: 'mean'})

            # Now add the confidence interval columns
            ci_df['lower_bound'] = ci_df['mean'] - interval
            ci_df['upper_bound'] = ci_df['mean'] + interval

            # Reorder columns to match your desired output
            ci_df = ci_df[['lower_bound', 'mean', 'upper_bound']]
            
            self.confidence_intervals[key] = ci_df
    
    # ----------------- Summary Functions -----------------    
    def _summary_helper(self, title:str, headers: list[str], table: pd.DataFrame):
        """
        Helper function to print a summary table.
        """
        print(f"\n{'-' * 20}")
        print(f"{title:^20}")
        print(f"{'-' * 20}")

        # Print the column headers
        print(" ".join(f"{header:<15}" for header in headers))

        # Print each row in the table with its string index
        for idx, row in table.iterrows():
            values = [f"{idx:<15}"] + [f"{row[col]:<15}" for col in table.columns]
            print(" ".join(values))

        print('\n')

    def anova_summary(self):
        """
        Print a summary of the ANOVA results, including string indices.
        """

        # Print the column headers
        headers = [''] + [col for col in self.anova_table.columns]

        self._summary_helper("ANOVA Table", headers, self.anova_table)

    def variance_summary(self):
        """
        Print a summary of the variance components.
        """

        variance_table = self.anova_table[['Variance']]
        headers = [''] + [col for col in variance_table.columns]

        self._summary_helper("Variance Components", headers, variance_table)

    def g_coeff_summary(self):
        """
        Print a summary of the g_coeff results
        """
        # Adjust the column headers for prettier printing
        headers = [''] + [col for col in self.g_coeffs_table.columns]
        symbol_map = {"rho^2": "ρ²", "phi^2": "φ²"}
        adjusted_headers = [symbol_map.get(header, header) for header in headers]

        self._summary_helper("G Coefficients", adjusted_headers, self.g_coeffs_table)
    
    def d_study_summary(self):
        """
        Print a summary of the D-Study results.
        """
        
        for label, d_study_df in self.d_study_dict.items():
            # Adjust the column headers for prettier printing
            title = f"D-Study: {label}"
            # Adjust the column headers for prettier printing
            # Add a blank space for the index column
            headers = [''] + [col for col in d_study_df.columns]
            symbol_map = {"rho^2": "ρ²", "phi^2": "φ²"}
            adjusted_headers = [symbol_map.get(header, header) for header in headers]

            self._summary_helper(title, adjusted_headers, d_study_df)
                
    ## POTENTIAL TODO: Add a D-Study visualization function to visualize the G-Coefficients for different scenarios

    def confidence_interval_summary(self):
        """
        Print a summary of the confidence intervals for each facet.
        """
        # Calculate the percentiles based on alpha
        lower_percentile = f"{(self._alpha/2)*100:.1f}%"
        upper_percentile = f"{(1-self._alpha/2)*100:.1f}%"
        
        for facet, ci_df in self.confidence_intervals.items():
            # Create a copy with renamed columns
            display_df = ci_df.copy()
            
            # Rename columns to show percentiles
            if 'lower_bound' in display_df.columns and 'upper_bound' in display_df.columns:
                display_df = display_df.rename(columns={
                    'lower_bound': lower_percentile,
                    'upper_bound': upper_percentile
                })
            
            # Handle MultiIndex by converting to string representation
            if isinstance(display_df.index, pd.MultiIndex):
                # Create string representations for each MultiIndex entry
                index_names = display_df.index.names
                string_indices = []
                
                for idx_tuple in display_df.index:
                    parts = [f"{name}={val}" for name, val in zip(index_names, idx_tuple)]
                    string_indices.append(', '.join(parts))
                
                # Create new DataFrame with string index
                display_df = pd.DataFrame(
                    display_df.values, 
                    index=string_indices, 
                    columns=display_df.columns
                )
            
            # Prepare headers (include 'Group' for the index column)
            headers = ['Group'] + list(display_df.columns)
            
            # Call the helper function with appropriate title
            self._summary_helper(f"{int((1-self._alpha)*100)}% CI for '{facet}'", headers, display_df)
        