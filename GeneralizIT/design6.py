# ----------- #
# Description:
# This script performs the ANOVA test on the A6 dataset.
# The generic design is i:(p x h)
# p and h have independent levels
# i is nested within both
# ----------- #

import pandas as pd
import numpy as np

# ---------------- #
# Let's Make This a Design Class
# ---------------- #

from design import Design

class Design6(Design):
    def __init__(self, data, corollary_df):
        super().__init__(data, corollary_df)
        self.get_unique_levels()
    
    def get_unique_levels(self):
        self.levels = {}

        self.levels[self.corollary_df['p']] =self.data[self.corollary_df['p']].nunique()
        self.levels[self.corollary_df['h']] =self.data[self.corollary_df['h']].nunique()

        # Since 'i' is nested within 'p' x 'h', we must consider the number of unique values for 'i' within each level of 'p' x 'h'
        p_name = self.corollary_df['p']
        h_name = self.corollary_df['h']
        i_name = self.corollary_df['i']
        n_i =self.data.groupby([p_name, h_name])[i_name].nunique()
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
        # ph    (n_p-1)(n_h-1)
        # i:ph  n_h*n_p(n_i-1)
        # ---------------- #
        
        # Let's get the degrees of freedom
        self.deg_freedom = {
            self.corollary_df['p']: self.levels[self.corollary_df['p']] - 1,
            self.corollary_df['h']: self.levels[self.corollary_df['h']] - 1,
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': (self.levels[self.corollary_df['p']] - 1) * (self.levels[self.corollary_df['h']] - 1),
            f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})': self.levels[self.corollary_df['h']] * self.levels[self.corollary_df['p']] * (self.levels[self.corollary_df['i']] - 1)
        }
    
    def _calculate_T_values(self):
        # ---------------- #
        # Perform the ANOVA
        # a     T(a)
        # p     n_i*n_h*sum(X_p^2)
        # h     n_p*n_i*sum(X_h^2)
        # ph    n_i*sum(X_ph^2)
        # i:ph  sum(X_i:ph^2)
        # ---------------- #
        
        # Get the T values
        self.T = {
            'u':self.data['Response'].count() *self.data['Response'].mean() ** 2,
            self.corollary_df['p']: np.sum(self.data.groupby(self.corollary_df['p'])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']] * self.levels[self.corollary_df['h']],
            self.corollary_df['h']: np.sum(self.data.groupby(self.corollary_df['h'])['Response'].mean() ** 2) * self.levels[self.corollary_df['p']] * self.levels[self.corollary_df['i']],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['h']])['Response'].mean() ** 2) * self.levels[self.corollary_df['i']],
            f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})': np.sum(self.data.groupby([self.corollary_df['p'], self.corollary_df['h'], self.corollary_df['i']])['Response'].mean() ** 2)
        }
    
    def _calculate_sums_of_squares(self):
        # ---------------- #
        # Perform the ANOVA
        # a     SS(a)
        # p     T(p) - T(u)
        # h     T(h) - T(u)
        # ph    T(ph) - T(p) - T(h) + T(u)
        # i:ph  T(i:ph) - T(ph)
        # ---------------- #
        
        # Get the SS values
        self.SS = {
            self.corollary_df['p']: self.T[self.corollary_df['p']] - self.T['u'],
            self.corollary_df['h']: self.T[self.corollary_df['h']] - self.T['u'],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': self.T[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] - self.T[self.corollary_df['p']] - self.T[self.corollary_df['h']] + self.T['u'],
            f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})': self.T[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})'] - self.T[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}']
        }
    
    def _calculate_mean_squares(self):
        # ---------------- #
        # MS(a) = SS(a) / df(a)
        # ---------------- #
        
        # Get the MS values (Mean Squares) this is SS/df
        self.MS = {
            self.corollary_df['p']: self.SS[self.corollary_df['p']] / self.deg_freedom[self.corollary_df['p']],
            self.corollary_df['h']: self.SS[self.corollary_df['h']] / self.deg_freedom[self.corollary_df['h']],
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': self.SS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] / self.deg_freedom[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'],
            f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})': self.SS[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})'] / self.deg_freedom[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})']
        }
    
    def _calculate_variance(self):
        # ---------------- #
        # Calculate the variances Appendix B.6 in Brennan (2001)
        # a     sigma^2(a)
        # p     [MS(p) - MS(ph)]/(n_i*n_h)
        # h     [MS(h) - MS(ph)]/(n_p*n_i)
        # ph    [MS(ph) - MS(i:ph)]/n_i
        # pi:h  MS(pi:h)
        # ---------------- #
        
        self.variances = {
            self.corollary_df['p']: (self.MS[self.corollary_df['p']] - self.MS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}']) / (self.levels[self.corollary_df['i']] * self.levels[self.corollary_df['h']]),
            self.corollary_df['h']: (self.MS[self.corollary_df['h']] - self.MS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'])  / (self.levels[self.corollary_df['p']] * self.levels[self.corollary_df['i']]),
            f'{self.corollary_df["p"]} x {self.corollary_df["h"]}': (self.MS[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] - self.MS[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})']) / self.levels[self.corollary_df['i']],
            f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})': self.MS[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})']
        }
    
    def calculate_anova(self):
        # ---------------- #
        # Perform the ANOVA
        # a     df                  T(a)                        SS(a)
        # p     n_p-1               n_i*n_h*sum(X_p^2)          T(p) - T(u)
        # h     n_h-1               n_p*n_i*sum(X_h^2)          T(h) - T(u)
        # ph    (n_p-1)(n_h-1)      n_i*sum(X_ph^2)             T(ph) - T(p) - T(h) + T(u)
        # i:ph  n_h*n_p(n_i-1)      sum(X_i:ph^2)               T(i:ph) - T(ph)
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
        # a     Tau(a)      delta(a): indices not in Tau/(levels not in Tau)    Delta(a): all indices not in Tau/(levels not in Tau)
        # p     sigma^2(p)  sigma^2(ph)/n_h + sigma^2(i:ph)/(n_h*n_i)           delta(p) + sigma^2(h)/(n_h)
        # h     sigma^2(h)  sigma^2(ph)/n_p + sigma^2(i:ph)/(n_p*n_i)           delta(h) + sigma^2(p)/(n_p)
        # ---------------- #
        
        # Make the Tau, delta, and Delta dictionary
        Tau_dict = {
            self.corollary_df['p']: self.variances[self.corollary_df['p']],
            self.corollary_df['h']: self.variances[self.corollary_df['h']],
        }

        delta_dict = {
            self.corollary_df["p"] : self.variances[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] / self.levels[self.corollary_df['h']] + self.variances[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})'] / (self.levels[self.corollary_df['h']] * self.levels[self.corollary_df['i']]),
            self.corollary_df['h']: self.variances[f'{self.corollary_df["p"]} x {self.corollary_df["h"]}'] / self.levels[self.corollary_df['p']] + self.variances[f'{self.corollary_df["i"]}:({self.corollary_df["p"]} x {self.corollary_df["h"]})'] / (self.levels[self.corollary_df['p']] * self.levels[self.corollary_df['i']])
        }

        Delta_dict = {
            self.corollary_df['p']: delta_dict[self.corollary_df['p']] + self.variances[self.corollary_df['h']] / self.levels[self.corollary_df['h']],
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