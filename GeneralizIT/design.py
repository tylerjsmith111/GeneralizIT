# -------------------------------- #
# Description:
# This script forms the generic design class for performing G and D study calculations.
# -------------------------------- #

import pandas as pd
import numpy as np
from itertools import product
from itertools import product
from scipy.stats import norm
import copy
import re

class Design:
    def __init__(self, data, corollary_df):
        self.data = data
        self.corollary_df = corollary_df
        self.anova_table = None
        self.g_coeff_table = None
        self.d_study_table = None
        self.confidence_intervals = None
        self.levels = {}
        self.deg_freedom = {}
        self.T = {}
        self.SS = {}
        self.MS = {}
        self.variances = {}
        
        
    def get_unique_levels(self):
        pass
    
    def calculate_anova(self):
        pass
    
    def _calculate_degrees_of_freedom(self):
        pass
    
    def _calculate_T_values(self):
        pass
    
    def _calculate_sums_of_squares(self):
        pass
    
    def _calculate_mean_squares(self):
        pass
    
    def _calculate_variance(self):
        pass
    
    def _calculate_g_coeffs(self):
        pass
    
    def g_coeffs(self):
        """
        Calculate G coefficients for the given data.
        This method calculates the G coefficients (rho^2 and phi^2) based on the provided data.
        It constructs Tau, delta, and Delta dictionaries using the variances and levels from the corollary dataframe.
        The G coefficients are then computed and stored in a DataFrame.
        The G coefficients are calculated as follows:
        - Tau(a): Variance of the source of variation 'a'.
        - delta(a): Sum of the variances of the interactions involving 'a' divided by the levels of the other factors.
        - Delta(a): Sum of delta(a) and the variances of the other factors divided by their respective levels.
        The G coefficients (rho^2 and phi^2) are computed using the formulas:
        - rho^2 = Tau(a) / (Tau(a) + delta(a))
        - phi^2 = Tau(a) / (Tau(a) + Delta(a))
        The results are stored in a DataFrame with the following columns:
        - 'Source of Variation': The source of variation (e.g., 'p', 'h').
        - 'Fixed': Placeholder for fixed effects (currently set to '---').
        - 'Random': The random effects (other variables not the object of measurement).
        - 'rho^2': The calculated rho^2 value.
        - 'phi^2': The calculated phi^2 value.
        Attributes:
        - g_coeff_table: DataFrame containing the G coefficients.
        """
        self.g_coeff_table = self._calculate_g_coeffs()
        
    # ----------------- D STUDY -----------------
    def calculate_d_study(self, levels: dict):
        """
        Implement the D-Study to determine the optimal number for each facet.
        
        Only applicable for maintaing a fully crossed design. Can be adapted in the 
        future to handle nested designs as well.
        
        D Study Implemented as in Brennan 2001, Generalizability Theory.
        Uses the G-Study learned variances and adjusts levels according to the users' input.

        Args:
            levels (dict): Dictionary of the number of levels for each facet in the D-Study.
            
            For example, if we have a 3 facet design, we can have the following levels:
            levels = {
                'person': [5, 10, 15],
                'item': [1, 2, 3],
                'rater': [2, 4, 6]
            }
            
            If we want to keep the levels the same pass None for the facet:
            levels = {
                'person': None,
                'item': [1, 2, 3],
                'rater': [2, 4, 6]
            }
        
        Returns:
            self.d_study_table (pd.DataFrame): A DataFrame containing the D-Study results. 
        """
        
        # First, normalize the keys in the levels dictionary
        levels = {re.sub(r"\s+", " ", key.strip().lower()): value for key, value in levels.items()}
        
        
        # Check that the levels dictionary contains only valid facets
        for key in levels.keys():
            if key not in self.levels.keys():
                raise ValueError(f"Facet {key} not found in the design. Please Update the levels dictionary to include only valid facets.")
                
        # Check that the levels dictionary contains list of integer values greater than 0
        for key, value in levels.items():
            if not isinstance(value, list) and value is not None:
                raise ValueError(f"Levels for facet {key} must be a list of integers or `None`. Please check the levels dictionary and try again.")
            if value is not None:
                if any([not isinstance(val, int) for val in value]):
                    raise ValueError(f"All levels for facet {key} must be integers. Please check the levels dictionary and try again.")
                if any([val <= 0 for val in value]):
                    raise ValueError(f"All levels for facet {key} must be greater than 0. Please check the levels dictionary and try again.")
            if value is None:
                levels[key] = [self.levels[key]]
                print(f"Levels for {key} not provided. Keeping the levels the same as the original design.")
        
        # Check to make sure all facets are accounted for
        if len(levels.keys()) != len(self.levels.keys()):
            # Get the missing facets
            missing_facets = [facet for facet in self.levels.keys() if facet not in levels.keys()]
            
            # Add the missing facets to the levels dictionary
            for facet in missing_facets:
                print(f"Facet {facet} not found in the levels dictionary. Keeping the levels the same as the original design.")
                levels[facet] = [self.levels[facet]]
                
        
        og_levels = copy.deepcopy(self.levels) # Store the original levels
        
        # Create a list of tuples containing all possible combinations of levels
        level_combinations = list(product(*levels.values()))
        
        self.d_study_table = pd.DataFrame()

        print("Using ANOVA Table Variance Dictionary for D-Study")
        variance_dict = self.anova_table.set_index('Source of Variation')['Variance Component'].to_dict()
        
        # Drop 'Total' from the dictionary if it exists
        variance_dict.pop('Total', None)
        
        # Clip any variance components that are negative to 0
        for key, value in variance_dict.items():
            if value < 0:
                variance_dict[key] = 0
                print(f"Variance component for {key} is negative. Setting to 0.")
        
        for combo in level_combinations:
            for i, key in enumerate(levels.keys()):
                if self.levels[key] != combo[i]:
                    print(f"Updating levels for {key} from {self.levels[key]} to {combo[i]}.")
                    self.levels[key] = combo[i]
            
            # calculate the generalizability coefficients
            d_coeffs = self._calculate_g_coeffs()
            
            # Create a DataFrame with the level combination values repeated for each row in d_coeffs
            combo_df = pd.DataFrame([combo] * len(d_coeffs), columns=levels.keys())
            
            # Concatenate the level combination DataFrame with the G Coefficients table
            combined_df = pd.concat([combo_df, d_coeffs], axis=1)
            
            # Append to the main study table
            self.d_study_table = pd.concat([self.d_study_table, combined_df], ignore_index=True)
           
         
        self.levels = copy.deepcopy(og_levels)  # Reset the levels to the original design
        
    # ----------------- Confidence Intervals -----------------
    def calculate_confidence_intervals(self, alpha: float=0.05, **kwargs):
        """Calculate the confidence intervals for the individual facets.
        This method computes the 95% confidence intervals for the individual facets using the formula from Cardinet et al. (1976).
        The formula for the confidence intervals is as follows:
        XaBC = XaBC +/- z_alpha/2 * sqrt(sigma^2(aBC))
        Args:
            alpha (float, optional): Significance level for the confidence intervals. Default is 0.05.
            
        Attributes:
            self.confidence_intervals (dict): A dictionary containing the % confidence intervals for each level of each facet.
        """
        # Check if the ANOVA table has been calculated
        if self.anova_table.empty:
            raise ValueError("Please calculate the ANOVA table using the calculate_anova method before calculating the confidence intervals.")
        
        
        self.confidence_intervals = {}
        
        var_table = self.anova_table.set_index('Source of Variation')['Variance Component'].to_dict()
        
        # Drop 'Total' from the dictionary
        if 'Total' in var_table.keys():
            var_table.pop('Total')
        
        # Clip any variance components that are negative to 0
        for key, value in var_table.items():
            if value < 0:
                print(f"Warning: Variance component for '{key}' was negative and has been clipped to 0.")
                var_table[key] = 0
        
        for key in var_table.keys():
            if ':' in key or ' x ' in key:
                continue  # Skip interaction effects
            
            # Sum the variances all other variances divided by the product of the levels of the other facets
            # Do not include the variance of the facet in question or the level of the facet in question
            # For example, sigma^2(aBC) = sigma^2(b)/n_b + sigma^2(c)/n_c + sigma^2(bc)/n_b*n_c + sigma^2(ab)/n_b + sigma^2(ac)/n_c + sigma^2(abc)/n_b*n_c
            sigma_squared = 0
            
            for var in var_table.keys():
                if var == key:
                    continue
                pi_star = 1
                
                for vars_n in self.levels.keys():
                    if vars_n in var and vars_n != key:
                        pi_star *= self.levels[vars_n]
                
                sigma_squared += var_table[var] / pi_star
            
            # Use the alpha value to get the z_alpha/2 value
            z_alpha = norm.ppf(1 - alpha/2)
            interval = z_alpha * np.sqrt(sigma_squared)

            # Get the means and unique values of the responses for the key
            means = self.data.groupby(key).mean().values.flatten()
            unique_values = self.data[key].unique()
            self.confidence_intervals[key] = {val: (m - interval, m, m + interval) for val, m in zip(unique_values, means)}
    
    # ----------------- Summary Functions -----------------    
    
    def anova_summary(self):
        """
        Print a summary of the ANOVA results.
        """
        print(f"\n{'-'*20}")
        print(f"{'ANOVA Table':^20}")
        print(f"{'-'*20}")
        print(f"{'Source':<20} {'SS':<15} {'DF':<5} {'MS':<15} {'Variance':<15}")
        for i, row in self.anova_table.iterrows():
            source = row['Source of Variation']
            ss = f"{row['Sum of Squares']:.4f}" if row['Sum of Squares'] is not None else ""
            df = f"{int(row['Degrees of Freedom'])}" if row['Degrees of Freedom'] is not None else ""
            ms = f"{row['Mean Square']:.4f}" if row['Mean Square'] is not None else ""
            variance = f"{row['Variance Component']:.4f}" if row['Variance Component'] is not None else ""
            # f_ratio = f"{row['F-Value']:.4f}" if row['F-Value'] is not None else ""
            print(f"{source:<20} {ss:<15} {df:<5} {ms:<15} {variance:<15}")
        print('\n')

    def variance_summary(self):
        """
        Print a summary of the variance components.
        """
        print(f"\n{'-'*20}")
        print(f"{'Variance Components':^20}")
        print(f"{'-'*20}")
        print(f"{'Source':<20} {'Variance Component':<20}")
        for i, row in self.anova_table.iterrows():
            source = row['Source of Variation']
            if source == 'Total':
                continue
            variance = f"{row['Variance Component']:.4f}" if row['Variance Component'] is not None else ""
            print(f"{source:<20} {variance:<20}")

    def g_coeff_summary(self):
        """
        Print a summary of the g_coeff results
        """
        print(f"\n{'-'*20}")
        print(f"{'G Coefficients':^20}") 
        print(f"{'-'*20}")
        print(f"{'Source of Variation':<20} {'random':<10} {'fixed':<10} {'rho^2':<10} {'phi^2':<10}")
        for i, row in self.g_coeff_table.iterrows():
            differentiation = row['Source of Variation']
            differentiation = differentiation.replace(' × ', ' & ')
            random = row['Generalized Over Random']
            random = random.replace(' × ', ' & ')
            fixed = row['Generalized Over Fixed']
            fixed = fixed.replace(' × ', ' & ')
            rho_squared = f"{row['rho^2']:.4f}" if row['rho^2'] is not None else ""
            phi_squared = f"{row['phi^2']:.4f}" if row['phi^2'] is not None else ""
            print(f"{differentiation:<20} {random:<10} {fixed:<10} {rho_squared:<10} {phi_squared:<10}")
    
    def d_study_summary(self):
        """
        Print a summary of the D-Study results.
        """
        
        # Identify unique combinations of levels (facet values) dynamically using self.facets
        unique_combinations = self.d_study_table[list(self.levels.keys())].drop_duplicates()

        for _, combo in unique_combinations.iterrows():
            # Extract the specific combination as a dictionary for easy access
            combo_dict = combo.to_dict()
            
            # Build a dynamic title based on the facets and their values in the current combination
            title_parts = [f"{facet}_n={value}" for facet, value in combo_dict.items()]
            title = f"G Coefficients ({', '.join(title_parts)})"
            print(f"\n{'-' * len(title)}")
            print(f"{title:^}")
            print(f"{'-' * len(title)}")
            
            # Filter rows matching this combination by dynamically constructing the filter
            filter_condition = (self.d_study_table[list(combo_dict)] == pd.Series(combo_dict)).all(axis=1)
            combo_rows = self.d_study_table[filter_condition]
            
            # Print column headers for the summary table
            print(f"{'Source of Variation':<20} {'random':<10} {'fixed':<10} {'rho^2':<10} {'phi^2':<10}")
            
            # Print each row for this combination
            for _, row in combo_rows.iterrows():
                differentiation = row['Source of Variation']
                differentiation = differentiation.replace(' × ', ' & ')
                random = row['Generalized Over Random']
                random = random.replace(' × ', ' & ')
                fixed = row['Generalized Over Fixed']
                fixed = fixed.replace(' × ', ' & ')
                rho_squared = f"{row['rho^2']:.4f}" if row['rho^2'] is not None else ""
                phi_squared = f"{row['phi^2']:.4f}" if row['phi^2'] is not None else ""
                print(f"{differentiation:<20} {random:<10} {fixed:<10} {rho_squared:<10} {phi_squared:<10}")
                
    ## POTENTIAL TODO: Add a D-Study visualization function to visualize the G-Coefficients for different scenarios

    def confidence_intervals_summary(self):
        """
        Print a summary of the confidence intervals.
        """
        print(f"\n{'-'*20}")
        print(f"{'Confidence Intervals':^20}")
        print(f"{'-'*20}")
        print(f"{'Source':<20} {'Identifier':<20} {'Confidence Interval':<40}")
        for key, intervals in self.confidence_intervals.items():
            for identifier, interval in intervals.items():
                print(f"{key:<20} {identifier:<20} {interval}")
        