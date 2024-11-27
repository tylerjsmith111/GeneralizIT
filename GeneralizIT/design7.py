# ----------- #
# Description:
# This script performs the ANOVA test on the A7 dataset.
# the general design is (i x h):p
# When you have nesting the number of levels for the nested factor is the number of unique values for each of the primary factor levels.
# In this case, p is independent, while n_levels for i and h are the number of unique values for each level of p.
# ----------- #

from design import Design
import pandas as pd
import numpy as np

class Design7(Design):
    def __init__(self, data, corollary_df):
        super().__init__(data, corollary_df)
        
        self.levels = self.get_unique_levels()
        
    def get_unique_levels(self):
        self.levels = {}

        self.levels[self.corollary_df['p']] =self.data[self.corollary_df['p']].nunique()

        # Both 'i' and 'h' are nested within 'p', we must consider the number of unique values for 'i' and 'h' within each level of 'p'
        p_name = self.corollary_df['p']
        h_name = self.corollary_df['h']
        i_name = self.corollary_df['i']
        n_i = self.data.groupby(p_name)[i_name].nunique()
        n_h = self.data.groupby(p_name)[h_name].nunique()
        # Check that the number of unique values are the same for each level of t
        if len(n_i.unique()) > 1:
            raise ValueError(f'The number of unique values for {self.corollary_df["i"]} within each level of {self.corollary_df["h"]} are not the same.')
        else:
            n_i = n_i.unique()[0]
            
        if len(n_h.unique()) > 1:
            raise ValueError(f'The number of unique values for {self.corollary_df["h"]} within each level of {self.corollary_df["p"]} are not the same.')
        else:
            n_h = n_h.unique()[0]
            
        self.levels[self.corollary_df['i']] = n_i
        self.levels[self.corollary_df['h']] = n_h
    
    def _calculate_degrees_of_freedom(self):
        # ---------------- #
        # Perform the ANOVA
        # a     df
        # p     n_p-1
        # i:p   n_p(n_i-1)
        # h:p   n_p(n_h-1)
        # ih:p  n_p(n_i-1)(n_h-1)
        # ---------------- #
        
        # Get the degrees of freedom
        self.deg_freedom = {
            self.corollary_df['p']: self.levels[self.corollary_df['p']] - 1,
            self.corollary_df['h']: self.levels[self.corollary_df['h']] - 1,
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.levels[self.corollary_df['p']] * (self.levels[self.corollary_df['i']] - 1),
            f'{self.corollary_df["h"]}:{self.corollary_df["p"]}': self.levels[self.corollary_df['p']] * (self.levels[self.corollary_df['h']] - 1),
            f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}': self.levels[self.corollary_df['p']] * (self.levels[self.corollary_df['i']] - 1) * (self.levels[self.corollary_df['h']] - 1)
        }
        
    
    def _calculate_T_values(self):
        # ---------------- #
        # Perform the ANOVA
        # a     T(a)
        # p     n_i*n_h*sum(X_p^2)
        # i:p   n_h*sum(X_i:p^2)
        # h:p   n_i*sum(X_ph^2)
        # ih:p  sum(X_ih:p^2)
        # ---------------- #
        
        # Get the T values
        self.T = {
            'u': self.data['Response'].count() * self.data['Response'].mean() ** 2,
            self.corollary_df['p']: np.sum(self.data.groupby(self.corollary_df['p'])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']] * self.levels[self.corollary_df['h']],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['i']])['Response'].mean() ** 2) * self.levels[self.corollary_df['h']],
            f'{self.corollary_df["h"]}:{self.corollary_df["p"]}': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['h']])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']],
            f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['i'], self.corollary_df['h']])['Response'].mean() ** 2)
        }
    
    def _calculate_sums_of_squares(self):
        # ---------------- #
        # Perform the ANOVA
        # a     SS(a)
        # p     T(p) - T(u)
        # i:p   T(i:p) - T(p)
        # h:p   T(h:p) - T(p)
        # ih:p  T(ih:p) - T(h:p) - T(i:p) + T(p)
        # ---------------- #
        
        # Get the SS values
        self.SS = {
            self.corollary_df['p']: self.T[self.corollary_df['p']] - self.T['u'],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.T[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] - self.T[self.corollary_df['p']],
            f'{self.corollary_df["h"]}:{self.corollary_df["p"]}': self.T[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'] - self.T[self.corollary_df['p']],
            f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}': self.T[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}'] - self.T[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'] - self.T[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] + self.T[self.corollary_df['p']]
        }
    
    def _calculate_mean_squares(self):
        # ---------------- #
        # MS(a) = SS(a)/df(a)
        # ---------------- #
        
        # Get the MS values (Mean Squares) this is SS/df
        self.MS = {
            self.corollary_df['p']: self.SS[self.corollary_df['p']] / self.deg_freedom[self.corollary_df['p']],
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': self.SS[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] / self.deg_freedom[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'],
            f'{self.corollary_df["h"]}:{self.corollary_df["p"]}': self.SS[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'] / self.deg_freedom[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'],
            f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}': self.SS[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}'] / self.deg_freedom[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}']
        }
    
    def _calculate_variance(self):
        # ---------------- #
        # Calculate the variances Appendix B.4 in Brennan (2001)
        # a     sigma^2(a)
        # p     [MS(p) - MS(h:p) - MS(i:p) + MS(ih:p)]/(n_h*n_i)     
        # i:p   [MS(i:p) - MS(ih:p)]/n_h
        # h:p    [MS(h:p) - MS(ih:p)]/n_i
        # ih:p  MS(ih:p)
        # ---------------- #
        
        # Get the variances
        self.variances = {
            self.corollary_df['p']: (self.MS[self.corollary_df['p']] - self.MS[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'] - self.MS[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] + self.MS[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}']) / (self.levels[self.corollary_df['h']] * self.levels[self.corollary_df['i']]),
            f'{self.corollary_df["i"]}:{self.corollary_df["p"]}': (self.MS[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] - self.MS[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}']) / self.levels[self.corollary_df['h']],
            f'{self.corollary_df["h"]}:{self.corollary_df["p"]}': (self.MS[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'] - self.MS[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}']) / self.levels[self.corollary_df['i']],
            f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}': self.MS[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}']
        }
    
    def calculate_anova(self):
        # ---------------- #
        # Perform the ANOVA
        # a     df                  T(a)                        SS(a)
        # p     n_p-1               n_i*n_h*sum(X_p^2)          T(p) - T(u)
        # i:p   n_p(n_i-1)          n_h*sum(X_i:p^2)            T(i:p) - T(p)
        # h:p    n_p(n_h-1)         n_i*sum(X_ph^2)             T(h:p) - T(p)
        # ih:p  n_p(n_i-1)(n_h-1)   sum(X_ih:p^2)               T(ih:p) - T(h:p) - T(i:p) + T(p)
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
    
    def _calculate_g_coeffs(self):
        # ---------------- #
        # To calculate G coefficients, we need to make a Tau, delta, and Delta dictionary
        # a     Tau(a)      delta(a): indices not in Tau/(levels not in Tau)                    Delta(a): all indices not in Tau/(levels not in Tau)
        # p     sigma^2(p)  sigma^2(h:p)/n_h + sigma^2(i:p)/(n_i) + sigma^2(ih:p)/(n_h*n_i)    delta(p)
        # ---------------- #
        
        # Make the Tau, delta, and Delta dictionary
        Tau_dict = {
            self.corollary_df['p']: self.variances[self.corollary_df['p']],
        }

        delta_dict = {
            self.corollary_df["p"] : self.variances[f'{self.corollary_df["h"]}:{self.corollary_df["p"]}'] / self.levels[self.corollary_df['h']] + self.variances[f'{self.corollary_df["i"]}:{self.corollary_df["p"]}'] / self.levels[self.corollary_df['i']] + self.variances[f'({self.corollary_df["i"]} x {self.corollary_df["h"]}):{self.corollary_df["p"]}'] / (self.levels[self.corollary_df['h']] * self.levels[self.corollary_df['i']]),
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