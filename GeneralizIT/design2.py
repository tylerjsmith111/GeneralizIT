# ----------- #
# Description:
# This script performs G study calculations for a single facet, Design 2, i:p
# the design is item:person
# When you have nesting the number of levels for the nested factor is the number of unique values for each of the primary factor levels.
# In this case, persons is independent so that would just be n_persons = 10.
# Since t is a primary factor, n_t = 3
# Since r is nested within t, we must consider the number of unique values for r within each level of t.
# ----------- #

import pandas as pd
import numpy as np
import scipy.stats as stats
from design_utils import parse_facets

# ---------------- #
# Inherit from the Design class
# ---------------- #
from design import Design

class Design2(Design):
    def __init__(self, data, corollary_df):
        super().__init__(data, corollary_df)
        self.get_unique_levels()
        
    def get_unique_levels(self):
        """
        Calculate and store the number of unique levels for specified columns in the dataset.
        This method populates the `self.levels` dictionary with the number of unique values for 
        the columns specified in `self.corollary_df['p']` and `self.corollary_df['i']`. It first 
        calculates the number of unique values for the column `p`. Then, it calculates the number 
        of unique values for the column `i` within each level of `p`. If the number of unique values 
        for `i` is not consistent across all levels of `p`, it raises a ValueError.
        Raises:
            ValueError: If the number of unique values for `i` within each level of `p` are not the same.
        Attributes:
            self.levels (dict): A dictionary where keys are column names and values are the number of unique values.
        """
        self.levels = {}

        self.levels[self.corollary_df['p']] = self.data[self.corollary_df['p']].nunique()

        # Since 'i' is nested within 'p', we must consider the number of unique values for 'i' within each level of 'p'
        # Get the number of unique values for i within each level of p
        p_name = self.corollary_df['p']
        i_name = self.corollary_df['i']
        n_i = self.data.groupby(p_name)[i_name].nunique()
        print(n_i)
        # Check that the number of unique values are the same for each level of t
        if len(n_i.unique()) > 1:
            raise ValueError(f'The number of unique values for {self.corollary_df["i"]} within each level of {self.corollary_df["h"]} are not the same.')
        else:
            n_i = n_i.unique()[0]
            
        self.levels[self.corollary_df['i']] = n_i
        
    def _calculate_degrees_of_freedom(self):
        # ---------------- #
        # Perform the ANOVA
        # a     df
        # p     n_p-1
        # i:p   n_p(n_i-1)
        # ---------------- #
        # Let's get the degrees of freedom
        self.deg_freedom = {
            self.corollary_df['p']: self.levels[self.corollary_df['p']] - 1,
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.levels[self.corollary_df['p']] * (self.levels[self.corollary_df['i']] - 1)
        }
        
    def _calculate_T_values(self):
        # ---------------- #
        # Perform the ANOVA
        # a     T(a)
        # p     n_i*sum(X_p^2)
        # i:p   sum(X_i:p^2)
        # ---------------- #
        
        # Get the T values
        self.T = {
            'u': self.data['Response'].count() * self.data['Response'].mean() ** 2,
            self.corollary_df['p']: np.sum(self.data.groupby(self.corollary_df['p'])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': np.sum(self.data.groupby([self.corollary_df['i'], self.corollary_df['p']])['Response'].mean() ** 2)
        }
        
    def _calculate_sums_of_squares(self):
        # ---------------- #
        # Perform the ANOVA
        # a     SS(a)
        # p     T(p) - T(u)
        # i:p   T(i:p) - T(p)
        # ---------------- #
        
        # Get the SS values
        self.SS = {
            self.corollary_df['p']: self.T[self.corollary_df['p']] - self.T['u'],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.T[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] - self.T[self.corollary_df["p"]]
        }
        
    def _calculate_mean_squares(self):
        # ---------------- #
        # Perform the ANOVA
        # a     MS(a)
        # p     SS(p) / df(p)
        # i:p   SS(i:p) / df(i:p)
        # ---------------- #
        
        self.MS = {
            self.corollary_df['p']: self.SS[self.corollary_df['p']] / self.deg_freedom[self.corollary_df['p']],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.SS[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] / self.deg_freedom[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}']
        }

    
    def _calculate_variance(self):
        # ---------------- #
        # Calculate the variances
        # a     sigma^2(a)
        # p     [MS(p) - MS(i:p)] / (n_i)
        # i:p   MS(i:p)
        # ---------------- #
        
        # Get the variances
        self.variances = {
            self.corollary_df['p']: (self.MS[self.corollary_df['p']] - self.MS[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}']) / self.levels[self.corollary_df['i']],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.MS[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}']
        }
        
    def calculate_anova(self):
        """
        Calculate the Analysis of Variance (ANOVA) for the given data.
        This method performs the following steps:
        1. Calculate degrees of freedom.
        2. Calculate T values.
        3. Calculate sums of squares.
        4. Calculate mean squares.
        5. Calculate variance components.
        Finally, it compiles the ANOVA table into a pandas DataFrame with the following columns:
        - 'Source of Variation': The source of variation.
        - 'Degrees of Freedom': The degrees of freedom for each source.
        - 'Sum of Squares': The sum of squares for each source.
        - 'Mean Square': The mean square for each source.
        - 'Variance Component': The variance component for each source.
        Note: Hypothesis testing is not an integral part of G-Theory, thus no F-Statistic is calculated.
        Attributes:
            anova_table (pd.DataFrame): The ANOVA table compiled into a pandas DataFrame
        """
        # ---------------- #
        # Perform the ANOVA
        # a     df                  T(a)                        SS(a)
        # p     n_p-1               n_i*sum(X_p^2)              T(p) - T(u)
        # i:p   n_p(n_i-1)          sum(X_i:p^2)                T(i:p) - T(p)
        # ---------------- #
        
        self._calculate_degrees_of_freedom()
        self._calculate_T_values()
        self._calculate_sums_of_squares()
        self._calculate_mean_squares()
        self._calculate_variance()
        
        # Compile ANOVA table
        self.anova_table = pd.DataFrame({
            'Source of Variation': list(self.deg_freedom.keys()),
            'Degrees of Freedom': list(self.deg_freedom.values()),
            'Sum of Squares': list(self.SS.values()),
            'Mean Square': list(self.MS.values()),
            'Variance Component': list(self.variances.values())
        })  # Hypothesis Testing is not an integral part of G-Theory thus no F-Statistic is calculated
    
    
    def _calculate_g_coeffs(self) -> pd.DataFrame:
        """
        Calculate the G coefficients for the given data.
        This method computes the G coefficients, which include rho and phi values, 
        based on the provided corollary data frame and variances. The results are 
        returned in a pandas DataFrame.
        Returns:
            pd.DataFrame: A DataFrame containing the G coefficients with columns:
                - 'Source of Variation': The source of variation (key).
                - 'Generalized Over Fixed': Placeholder for fixed effects (currently '---').
                - 'Generalized Over Random': The random effects not being measured.
                - 'rho^2': The rho coefficient.
                - 'phi^2': The phi coefficient.
        """
        # ---------------- #
        # Calculate the G coefficients
        # a     Tau(a)      delta(a): indices not in Tau/(levels not in Tau)    Delta(a): all indices not in Tau/(levels not in Tau)
        # p     sigma^2(p)  sigma^2(i:p)/n_i                                    delta(p)
        # ---------------- #
        
        # Make the Tau, delta, and Delta dictionary
        Tau_dict = {
            self.corollary_df['p']: self.variances[self.corollary_df['p']],
        }

        delta_dict = {
            self.corollary_df["p"] : self.variances[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] / self.levels[self.corollary_df['i']]
        }

        Delta_dict = {
            self.corollary_df['p']: delta_dict[self.corollary_df['p']]
        }
        
        # Get the G coefficients
        g_coeff_df = pd.DataFrame(columns=['Source of Variation', 'Generalized Over Fixed', 'Generalized Over Random', 'rho^2', 'phi^2'])
        
        for i, key in enumerate(Tau_dict.keys()):
            rho = Tau_dict[key] / (Tau_dict[key] + delta_dict[key] + 1e-8)  # Add a small value to avoid division by zero
            phi = Tau_dict[key] / (Tau_dict[key] + Delta_dict[key] + 1e-8)  # Add a small value to avoid division by zero
            
            # The random effects are the other variables that are not the object of measurement
            random_effects = [k for k in self.corollary_df.values() if k != key]
            
            # Join the random effects
            random_effects = ' & '.join(random_effects)
            
            g_coeff_df.loc[i] = [key, '---', random_effects, rho, phi]
            
        return g_coeff_df
        
        
        
# if __name__ == "__main__":
#     # Load the csv file syndata2.csv
#     df = pd.read_csv('syndata2.csv')

#     print(df.head())

#     # New DataFrame with columns 'person', 't', 'r', 'Response'
#     new_data = {
#         'person': [],
#         'item': [],
#         'Response': []
#     }

#     # Populate the new DataFrame
#     for person in range(1, 11):
#         for item in range(1, 9):
#             key = f'personi_item{item}'
            
#             if key in df.columns:
#                 response = df.at[person-1, key]
#                 new_data['person'].append(person)
#                 new_data['item'].append((person-1)*8 + item)
#                 new_data['Response'].append(response)

#     # Convert to DataFrame
#     formatted_df = pd.DataFrame(new_data)

#     print(formatted_df.head(10))

#     # Create the corollary df
#     corollary_df, design_num = parse_facets('item:person')
#     print(f"The corollary_df is: {corollary_df}")
#     print(f"The design number is: {design_num}")
#     design2 = Design2(formatted_df, corollary_df)
    
#     design2.calculate_anova()
    
#     design2.g_coeffs()
    
#     design2.g_coeff_summary()
#     design2.anova_summary()