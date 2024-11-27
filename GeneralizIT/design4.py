# ----------- #
# Description:
# This script performs the ANOVA test on the A4 dataset.
# Synthetic Data Set # 4
# the design is person x (r:t)
# When you have nesting the number of levels for the nested factor is the number of unique values for each of the primary factor levels.
# In this case, persons is independent so that would just be n_persons = 10.
# Since t is a primary factor, n_t = 3
# Since r is nested within t, we must consider the number of unique values for r within each level of t.
# ----------- #

import pandas as pd
import numpy as np

# ---------------- #
# Let's inherit from the Design class
# ---------------- #
from design import Design

class Design4(Design):
    def __init__(self, data, corollary_df):
        super().__init__(data, corollary_df)
        self.get_unique_levels()
        
    def get_unique_levels(self):
        self.levels = {}

        self.levels[self.corollary_df['p']] = self.data[self.corollary_df['p']].nunique()
        self.levels[self.corollary_df['h']] = self.data[self.corollary_df['h']].nunique()

        # Since 'i' is nested within 'h', we must consider the number of unique values for 'i' within each level of 'h'
        # Get the number of unique values for i within each level of h
        h_name = self.corollary_df['h']
        i_name = self.corollary_df['i']
        n_i = self.data.groupby(h_name)[i_name].nunique()
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
        # h     n_h-1              
        # i:h   n_h(n_i-1)         
        # ph    (n_p-1)(n_h-1)      
        # pi:h  n_h(n_p-1)(n_i-1)   
        # ---------------- #
        
        # Let's get the degrees of freedom
        self.deg_freedom = {
            self.corollary_df['p']: self.levels[self.corollary_df['p']] - 1,
            self.corollary_df['h']: self.levels[self.corollary_df['h']] - 1,
            f'{self.corollary_df["i"]}:{self.corollary_df["h"]}': self.levels[self.corollary_df['h']] * (self.levels[self.corollary_df['i']] - 1),
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': (self.levels[self.corollary_df['p']] - 1) * (self.levels[self.corollary_df['h']] - 1),
            f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})': self.levels[self.corollary_df['h']] * (self.levels[self.corollary_df['p']] - 1) * (self.levels[self.corollary_df['i']] - 1)
        }
    
    def _calculate_T_values(self):
        # ---------------- #
        # Perform the ANOVA
        # a                  T(a)                        
        # p                  n_i*n_h*sum(X_p^2)          
        # h                  n_p*n_i*sum(X_h^2)          
        # i:h                n_p*sum(X_i:h^2)            
        # ph                 n_i*sum(X_ph^2)             
        # pi:h               sum(X_pi:h^2)               
        # ---------------- #
        
        # Get the T values
        self.T = {
            'u': self.data['Response'].count() * self.data['Response'].mean() ** 2,
            self.corollary_df['p']: np.sum(self.data.groupby(self.corollary_df['p'])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']] * self.levels[self.corollary_df['h']],
            self.corollary_df['h']: np.sum(self.data.groupby(self.corollary_df['h'])['Response'].mean() ** 2) * self.levels[self.corollary_df['p']] * self.levels[self.corollary_df['i']],
            f'{self.corollary_df["i"]}:{self.corollary_df["h"]}': np.sum(self.data.groupby([self.corollary_df['h'], self.corollary_df['i']])['Response'].mean() ** 2) * self.levels[self.corollary_df['p']],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['h']])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']],
            f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['h'], self.corollary_df['i']])['Response'].mean() ** 2)
        }

    
    def _calculate_SS_values(self):
        # ---------------- #
        # Perform the ANOVA
        # a     SS(a)
        # p     T(p) - T(u)
        # h     T(h) - T(u)
        # i:h   T(i:h) - T(h)
        # ph    T(ph) - T(p) - T(h) + T(u)
        # pi:h  T(pi:h) - T(ph) - T(i:h) + T(h)
        # ---------------- #
        
        # Get the SS values
        self.SS = {
            self.corollary_df['p']: self.T[self.corollary_df['p']] - self.T['u'],
            self.corollary_df['h']: self.T[self.corollary_df['h']] - self.T['u'],
            f'{self.corollary_df["i"]}:{self.corollary_df["h"]}': self.T[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] - self.T[self.corollary_df['h']],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': self.T[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] - self.T[self.corollary_df['p']] - self.T[self.corollary_df['h']] + self.T['u'],
            f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})': self.T[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})'] - self.T[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] - self.T[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] + self.T[self.corollary_df['h']]
        }

    def _calculate_MS_values(self):
        # ---------------- #
        # MS(a) = SS(a)/deg_freedom(a)
        # ---------------- #
        
        # Get the MS values (Mean Squares) this is SS/df
        self.MS = {
            self.corollary_df['p']: self.SS[self.corollary_df['p']] / self.deg_freedom[self.corollary_df['p']],
            self.corollary_df['h']: self.SS[self.corollary_df['h']] / self.deg_freedom[self.corollary_df['h']],
            f'{self.corollary_df["i"]}:{self.corollary_df["h"]}': self.SS[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] / self.deg_freedom[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': self.SS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] / self.deg_freedom[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'],
            f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})': self.SS[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})'] / self.deg_freedom[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})']
        }

        
    def calculate_anova(self):
        # ---------------- #
        # Perform the ANOVA
        # a     df                  T(a)                        SS(a)
        # p     n_p-1               n_i*n_h*sum(X_p^2)          T(p) - T(u)
        # h     n_h-1               n_p*n_i*sum(X_h^2)          T(h) - T(u)
        # i:h   n_h(n_i-1)          n_p*sum(X_i:h^2)            T(i:h) - T(h)
        # ph    (n_p-1)(n_h-1)      n_i*sum(X_ph^2)             T(ph) - T(p) - T(h) + T(u)
        # pi:h  n_h(n_p-1)(n_i-1)   sum(X_pi:h^2)               T(pi:h) - T(ph) - T(i:h) + T(h)
        # ---------------- #
         
        self._calculate_degrees_of_freedom()
        self._calculate_T_values()
        self._calculate_SS_values()
        self._calculate_MS_values()
        self._calculate_variance()
        
        # Compile ANOVA table
        self.anova_table = pd.DataFrame({
            'Source of Variation': list(self.deg_freedom.keys()),
            'Degrees of Freedom': list(self.deg_freedom.values()),
            'Sum of Squares': list(self.SS.values()),
            'Mean Square': list(self.MS.values()),
            'Variance Component': list(self.variances.values())
        })  # Hypothesis Testing is not an integral part of G-Theory thus no F-Statistic is calculated
        
    
    def _calculate_variance(self):
        # ---------------- #
        # Calculate the variances Appendix B.4 in Brennan (2001)
        # a     sigma^2(a)
        # p     [MS(p) - MS(ph)]/(n_i*n_h)
        # h     [MS(h) - MS(ph) - MS(i:h) + MS(pi:h)]/(n_p*n_i)
        # i:h   [MS(i:h) - MS(pi:h)]/n_p
        # ph    [MS(ph) - MS(pi:h)]/n_i
        # pi:h  MS(pi:h)
        # ---------------- #
        
        # Get the variances
        self.variances = {
            self.corollary_df['p']: (self.MS[self.corollary_df['p']] - self.MS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}']) / (self.levels[self.corollary_df['i']] * self.levels[self.corollary_df['h']]),
            self.corollary_df['h']: (self.MS[self.corollary_df['h']] - self.MS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] - self.MS[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] + self.MS[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})'])  / (self.levels[self.corollary_df['p']] * self.levels[self.corollary_df['i']]),
            f'{self.corollary_df["i"]}:{self.corollary_df["h"]}': (self.MS[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] - self.MS[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})']) / self.levels[self.corollary_df['p']],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': (self.MS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] - self.MS[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})']) / self.levels[self.corollary_df['i']],
            f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})': self.MS[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})']
        }
    
    
    def _calculate_g_coeffs(self):
        # ---------------- #
        # To calculate G coefficients, we need to make a Tau, delta, and Delta dictionary
        # a     Tau(a)      delta(a): indices not in Tau/(levels not in Tau)    Delta(a): all indices not in Tau/(levels not in Tau)
        # p     sigma^2(p)  sigma^2(ph)/n_h + sigma^2(pi:h)/(n_h*n_i)           delta(p) + sigma^2(h)/(n_h) + sigma^2(i:h)/(n_h*n_i)
        # h     sigma^2(h)  sigma^2(ph)/(n_p) + sigma^2(i:h)/(n_i) + sigma^2(pi:h)/(n_p*n_i)          delta(h) + sigma^2(p)/(n_p)
        # ---------------- #
        
        # Make the Tau, delta, and Delta dictionary
        Tau_dict = {
            self.corollary_df['p']: self.variances[self.corollary_df['p']],
            self.corollary_df['h']: self.variances[self.corollary_df['h']],
        }

        delta_dict = {
            self.corollary_df["p"] : self.variances[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] / self.levels[self.corollary_df['h']] + self.variances[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})'] / (self.levels[self.corollary_df['h']] * self.levels[self.corollary_df['i']]),
            self.corollary_df['h']: self.variances[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] / self.levels[self.corollary_df['p']] + self.variances[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] / self.levels[self.corollary_df['i']] + self.variances[f'{self.corollary_df["p"]} x ({self.corollary_df["i"]}:{self.corollary_df["h"]})'] / (self.levels[self.corollary_df['p']] * self.levels[self.corollary_df['i']])
        }

        Delta_dict = {
            self.corollary_df['p']: delta_dict[self.corollary_df['p']] + self.variances[self.corollary_df['h']] / self.levels[self.corollary_df['h']] + self.variances[f'{self.corollary_df["i"]}:{self.corollary_df["h"]}'] / (self.levels[self.corollary_df['h']] * self.levels[self.corollary_df['i']]),
            self.corollary_df['h']: delta_dict[self.corollary_df['h']] + self.variances[self.corollary_df['p']] / self.levels[self.corollary_df['p']]
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
            
# if __name__ == '__main__':
#     # Load the csv file syndata4.csv
#     df = pd.read_csv('syndata4.csv')

#     print(df.head())

#     # New DataFrame with columns 'person', 't', 'r', 'Response'
#     new_data = {
#         'person': [],
#         't': [],
#         'r': [],
#         'Response': []
#     }

#     # Populate the new DataFrame
#     for person in range(1, 11):
#         for t in [1, 2, 3]:  # Assuming 't1', 't2', 't3'
#             for r in range(1, 13):  # Assuming 'r1' to 'r12'
#                 key = f't{t}_r{r}'
#                 # check if the key exists
#                 if key in df.columns:
#                     response = df.at[person-1, key]
#                     new_data['person'].append(person)
#                     new_data['t'].append(t)
#                     new_data['r'].append(r)
#                     new_data['Response'].append(response)

#     # Convert to DataFrame
#     formatted_df = pd.DataFrame(new_data)

#     print(formatted_df.head(10))

#     # Create the corollary df
#     corollary_df, design_num = parse_facets('person x (r:t)')
#     print(f"The corollary_df is: {corollary_df}")
#     print(f"The design number is: {design_num}")
    
#     # Create the Design4 object
#     design = Design4(formatted_df, corollary_df)
    
#     # Calculate the ANOVA
#     design.calculate_anova()
    
#     # Calculate the G coefficients
#     design.g_coeffs()
    
#     # Print the ANOVA table
#     design.anova_summary()
    
#     # Print the G coefficients
#     design.g_coeff_summary()
    