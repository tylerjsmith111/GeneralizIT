import copy
import re
import numpy as np
import pandas as pd
from scipy.stats import norm
from itertools import combinations
from itertools import product
from design import Design

class DesignCrossed(Design):
    def __init__(self, data: pd.DataFrame, corollary_df=None):
        super().__init__(data, corollary_df)
        response = 'Response'
        facets = self.data.columns
        
        # drop the response column
        facets = [f for f in facets if f != response]
        
        self.facets = self._check_facets_and_create_sources_of_variance(data, facets)
        self.response = self._check_response(data=data, response=response)
        self.data = self._prune_data(data)  # Prune the data to only include the necessary columns
        self.levels = self._get_levels()  # Get the levels for each facet
        
    def _check_facets_and_create_sources_of_variance(self, data: pd.DataFrame, facets: list[str]):
        """
        Check the facets are in the data and create the sources of variance for the study design.

        Args:
            data (pd.DataFrame): The input data as a pandas DataFrame.
            design (str): A string representing the design of the experiment. 
            
        Attributes:
            source_of_variance (dict): A dictionary containing the sources of variance for the study design. 
            The keys are the pretty printed sources of variance, and the values are tuples of the sources of variance.
            
            For example, for a 3 facet design, the sources of variance would be:
            {
                'A': ('A',),
                'B': ('B',),
                'C': ('C',),
                'A × B': ('A', 'B'),
                'A × C': ('A', 'C'),
                'B × C': ('B', 'C'),
                'A × B × C': ('A', 'B', 'C'),
                'Total': 'Total'
            }

        Returns:
            facets (tuple): A tuple of the facets present in the study design
        """
        # We have a completely crossed design such as a x b x c
        # This allows for all possible interactions between the factors
        # i.e. a, b, c, ab, ac, bc, abc
        
        # Check that the facets are columns in the DataFrame
        for facet in facets:
            if facet not in data.columns:
                raise ValueError(f"Facet '{facet}' not found in the data columns. Please check the facet names and try again.")
            elif data[facet].isnull().sum() > 0:
                raise ValueError(f"Facet '{facet}' contains missing values. Please check the facet and try again.")
        
        # If all facets are present in the data, convert the list to a tuple for immutability
        facets = tuple(facets)

        # Initialize an empty list to store variances
        source_of_variance = []
        source_of_variance_pretty = []
        
        # Loop through combinations of crossed design factors
        for r in range(1, len(facets) + 1):
            # Get all combinations of r elements
            for combo in combinations(facets, r):
                # append to variances
                source_of_variance.append(combo)
                
                source_of_variance_pretty.append(' × '.join(combo))
        
        source_of_variance.append('Total')
        source_of_variance_pretty.append('Total')
        
        
        self.source_of_variance = {}
        for i, variance in enumerate(source_of_variance):
            self.source_of_variance[source_of_variance_pretty[i]] = variance
        
        return facets
    
    def _check_response(self, data: pd.DataFrame, response: str):
        """
        Validates the response variable in the provided DataFrame.
        This method checks if the specified response variable exists in the DataFrame,
        is of a numeric type, contains no missing values, and ensures that the data
        is fully crossed based on the unique values of the facets.
        
        Args:
            data (pd.DataFrame): DataFrame containing the data.
            response (str): Column name of the response variable.
        Raises:
            ValueError: If the response variable is not found in the DataFrame columns.
            ValueError: If the response variable is not of a numeric type.
            ValueError: If the response variable contains missing values.
            ValueError: If the data is not fully crossed.
        Returns:
            str: The name of the response variable if all checks pass.
        """
        
        if response not in data.columns:
            raise ValueError(f"Response variable '{response}' not found in the data columns. Please check the response variable name and try again.")
        
        # Check that the response variable is a numeric type
        if data[response].dtype not in ['int64', 'float64']:
            raise ValueError(f"Response variable '{response}' must be a numeric type. Please check the response variable type and try again.")
        
        # Check that the data is not missing
        if data[response].isnull().sum() > 0:
            raise ValueError(f"Response variable '{response}' contains missing values. Please check the response variable and try again.")
        
        # Get the number of unique values for each facet
        unique_values = data[list(self.facets)].nunique().to_list()
        
        total_crossed_values = np.prod(unique_values)
        
        if total_crossed_values != data[response].shape[0]:
            raise ValueError(f"The data is not fully crossed. Please check the data and try again.")
        
        return response
        
    def _prune_data(self, data: pd.DataFrame):
        """
        Prunes the input DataFrame by dropping columns that are not in the list of facets or the response variable.

        Args:
            data (pd.DataFrame): The input DataFrame to be pruned.

        Returns:
            pd.DataFrame: The pruned DataFrame containing only the columns specified in facets and the response variable.
        """
        # Combine factors and response variable into a single list
        vars = list(self.facets) + [self.response]
        
        # Create a list of columns to drop
        drop_cols = [col for col in data.columns if col not in vars]
        
        # Create a warning message if any columns are dropped
        if len(drop_cols) > 0:
            print("Warning: The following columns have been dropped from the data:")
            for col in drop_cols:
                print(col)
        
        # Drop the columns
        data = data.drop(columns=drop_cols)
        
        return data
    
    def _get_levels(self):    
        """
        Computes the unique levels for each facet in the dataset.

        Returns:
            dict: A dictionary where keys are facet names and values are arrays of unique levels for each facet.
                  Additionally, includes the total number of observations with the key 'n'.
        """
        levels = {}
        for facet in self.facets:
            levels[facet] = self.data[facet].unique()
            if len(levels[facet]) == 0:
                raise ValueError(f"Facet '{facet}' has no unique levels. Please check the data and try again.")
            
        levels['n'] = self.data.shape[0]  # Total number of observations
        
        return levels
    
    def _calculate_T_values(self, overall_mean):
        
        """
        This helper function calculates the T values for each variance component.
        This is done according to Brennan 2001, Generalizability Theory.
        T(alpha) = pi(alpha_star) * sum(mean(alpha) ** 2)
        where pi(alpha_star) is the product of levels of all facets except alpha
        
        Args:
            overall_mean (float): The grand mean of the response variable.

        Returns:
            T (dict): A dictionary where the keys are the names of the variance components and the values are the corresponding T values.
        """
        
        T = {}
        
        # T(U) = n * sum(mean(U) ** 2), since all the product of all levels is n
        T['U'] = self.levels['n'] * (overall_mean ** 2)
        
        for key, variance_component in self.source_of_variance.items():
            if key == 'Total':
                T['Total'] = None
                continue
            if len(variance_component) == 1:
                # This is a main effect
                alpha = variance_component[0]
                
                # Get the levels for all facets except alpha
                pi_alpha_star = 1
                for facet in self.facets:
                    if facet != alpha:
                        pi_alpha_star *= len(self.levels[facet])
                
                # Calculate T(alpha)
                T[key] = pi_alpha_star * np.sum([self.data[self.data[alpha] == i][self.response].mean() ** 2 for i in self.levels[alpha]])
            else:
                # This is an interaction effect
                alpha = list(variance_component)
                
                # Get the levels for all facets except alpha
                pi_alpha_star = 1
                for facet in self.facets:
                    if facet not in alpha:
                        pi_alpha_star *= len(self.levels[facet])
                
                # Calculate T(alpha)
                interaction_means = self.data.groupby(alpha)[self.response].mean()
                
                T[key] = pi_alpha_star * np.sum([interaction_means[i] ** 2 for i in interaction_means.index])
        
        return T
    
    def _calculate_sums_of_squares(self, T):
        """
        Calculate the sum of squares for each variance component according to Brennan 2001, Generalizability Theory.
        This function computes the sum of squares (SS) for each variance component in the provided dictionary `T`. 
        The calculations are based on the following rules:
        - For main effects: SS(alpha) = T(alpha) - T(U)
        - For interaction effects: SS(alpha) = T(alpha) - (sum(T(beta) for beta in alpha) + sum(T(delta) for delta in beta) - ... + (-1)^n*T(U))
        - For the total effect: SS(Total) = T(highest_order_interaction) - T(U)
        Args:
            T (dict): A dictionary containing the variance components. The keys represent the components, and the values are their respective T values.
        Returns:
            SS (dict): A dictionary containing the sum of squares for each variance component.
        """
        
        SS = {}
        for key, t_value in T.items():
            if key == 'U':
                continue
            if key == 'Total':
                # The highest order interaction e.g T(ABC) - T(U)
                # find the longest key in the T dictionary that is not 'Total'
                longest_key = max([key for key in T.keys() if key != 'Total'], key=len)
                
                SS['Total'] = T[longest_key] - T['U']
            else:
                if len(self.source_of_variance[key]) == 1:
                    # This is a main effect
                    # SS(alpha) = T(alpha) - T(U)
                    
                    SS[key] = t_value - T['U']
                else:
                    # This is an interaction effect
                    # SS(alpha) = T(alpha) - (sum(T(beta) for beta in alpha) + sum(T(delta) for delta in beta) - ... + (-1)^n*T(U))
                    # For example, SS(AB) = T(AB) - (T(A) + T(B)) + T(U)
                    interaction_ss = t_value
                    facet_interactions = list(self.source_of_variance[key]) # for ex 'abc' is given by ['a', 'b', 'c']
                    # Get all possible combinations involving 2 facets
                    for r in range(1, len(facet_interactions)):
                        # Get the T value for the interaction at that level
                        combo_sum = 0
                        for combo in combinations(facet_interactions, (len(facet_interactions) - r)):
                            # print(f"COMBO: {combo}")
                            # print(f"T value: {T[' × '.join(combo)]}")
                            combo_sum += T[' × '.join(combo)]
                        interaction_ss += ((-1) ** r) * combo_sum
                                                
                    # Finally add the (-1)^n*T(U) value to the interaction sum of squares
                    interaction_ss += ((-1) ** len(facet_interactions)) * T['U']
                    
                    SS[key] = interaction_ss
        
        return SS
    
    def _calculate_degrees_of_freedom(self):
        """
        This method computes the degrees of freedom for each source of variance
        in the model. The degrees of freedom are calculated based on the levels
        of each variance component.
        Returns:
            dict: A dictionary where the keys are the names of the variance 
                  components and the values are the corresponding degrees of freedom.
        """
        
        degrees_of_freedom = {}
        
        for key, variance_component in self.source_of_variance.items():
            if key == 'Total':
                degrees_of_freedom['Total'] = self.levels['n'] - 1
            elif len(variance_component) == 1:
                # This is a main effect
                degrees_of_freedom[key] = len(self.levels[variance_component[0]]) - 1
            else:
                # This is an interaction effect
                degrees_of_freedom[key] = np.prod([len(self.levels[facet]) - 1 for facet in variance_component])
                
            # The degrees of freedom should always be >= 1
            if degrees_of_freedom[key] < 1:
                raise ValueError(f"Degrees of freedom for '{key}' is less than 1. Please check the data and try again.")
        
        return degrees_of_freedom
    
    def _calculate_mean_squares(self, SS, degrees_of_freedom):
        """
        Calculate the mean square for each variance component.
        
        Parameters:
        SS (dict): A dictionary containing the sum of squares for each variance component.
        degrees_of_freedom (dict): A dictionary containing the degrees of freedom for each variance component.
        
        Returns:
        dict: A dictionary containing the mean square for each variance component.
        """
        
        mean_square = {}
        
        for key, ss_value in SS.items():        
            mean_square[key] = ss_value / degrees_of_freedom[key]
        
        return mean_square
                    
    def calculate_anova(self):
        
        """
        Calculate the Analysis of Variance (ANOVA) table for the given data.
        This method calculates the overall mean, variance components, sum of squares,
        degrees of freedom, and mean square for the data. It compiles these values into
        an ANOVA table and calculates the variance components using corrected formulas.
        
        Returns:
            pd.DataFrame: A DataFrame containing the ANOVA table with the following columns:
                - 'Source of Variation': The source of variance.
                - 'Degrees of Freedom': The degrees of freedom for each source of variance.
                - 'Sum of Squares': The sum of squares for each source of variance.
                - 'Mean Square': The mean square for each source of variance.
                - 'Variance Component': The variance component for each source of variance.
        Note:
            Hypothesis testing is not an integral part of Generalizability Theory (G-Theory),
            thus no F-Statistic is calculated in this method.
        """    
        # Calculate overall mean
        overall_mean = self.data[self.response].mean()
        
        # Let's calculate the variance components using the general formulas
        T = self._calculate_T_values(overall_mean)
        SS = self._calculate_sums_of_squares(T)
        degrees_of_freedom = self._calculate_degrees_of_freedom()
        mean_square = self._calculate_mean_squares(SS, degrees_of_freedom)
        
        # Compile ANOVA table
        self.anova_table = pd.DataFrame({
            'Source of Variation': list(self.source_of_variance.keys()),
            'Degrees of Freedom': list(degrees_of_freedom.values()),
            'Sum of Squares': list(SS.values()),
            'Mean Square': list(mean_square.values()),
        })  # Hypothesis Testing is not an integral part of G-Theory thus no F-Statistic is calculated
        
        # Calculate variance components using the corrected formulas
        variance_dict = self._calculate_variance_components(mean_square)

        # Add the variance components to the ANOVA table
        variance_components_list = []
        for key in self.anova_table['Source of Variation'].values:
            if key in variance_dict.keys():
                variance_components_list.append(variance_dict[key])
            else:
                variance_components_list.append(None)
        
        self.anova_table['Variance Component'] = variance_components_list

        return self.anova_table
    
    def _calculate_variance_components(self, mean_squares):
        """
        Calculate variance components using the general formulas.
        variance(alpha) = 1/pi(alpha_star) * [linear combination of mean squares],
        pi(alpha_star) is the product of levels of all facets except alpha
        where the linear combination of mean squares is determined by the following algorithm: 
        step 0: MS(alpha);
        step 1: minus mean squares for all components that consist of t indices in alpha and exactly one of the indices in A;
        step 2: Plus mean squares for all components that consist of t indices in alpha and any two of the indices in A; 
        .
        .
        .
        step n: Plus (-1)^n*[mean squares for all components that consist of t indices in alpha and n of indices in A]
        
        For example, variance(A) = [MS(A) - MS(AB) - MS(AC) + MS(ABC)] / (b * c)      
        """
        
        adjusted_variance_dict = {}
        
        for key in mean_squares.keys():
            if key == 'Total':
                continue
            
            alpha = list(self.source_of_variance[key])
            pi_alpha_star = 1
            for facet in self.facets:
                if facet not in alpha:
                    pi_alpha_star *= len(self.levels[facet])
            
            # Counters and Adjusted Variance
            # The counter is used to keep track of the number of indices for positive or negative
            counter = 0 # start from 0 as the first iteration is just the MS of the value itself which is positive
            adjusted_variance = 0 # initialize counter for adjusted_variance
            # This gives us the range for possible interaction indices starting from the mean square for the facet
            # i.e. MS(A) for the facet A we would start with -MS(AB) - MS(AC), then +MS(ABC)
            for i in range(len(alpha), len(self.facets) + 1):
                # Get the source of variance that has the same number of indices as i
                # and contains all the indices in alpha
                source = [variance for variance in self.source_of_variance.values() if len(variance) == i and all([index in variance for index in alpha])]
                # print(f"Source: {source}")
                
                for interaction in source:
                    # print(f"Interaction: {interaction}")
                    # Get the mean square value for the interaction
                    interaction_ms = mean_squares[' × '.join(interaction)]
                    # print(f"Interaction MS: {interaction_ms}")
                    # print(f"Counter {counter}, Positive or Negative: {((-1) ** counter)}")
                    adjusted_variance += ((-1) ** counter) * interaction_ms
                
                adjusted_variance_dict[key] = adjusted_variance / pi_alpha_star
                counter += 1  # increment the counter for the next iteration
        
        return adjusted_variance_dict
                    
    # ----------------- G Coefficients -----------------
    def g_coeff_general(self, variance_dict):
        """
        Create a table of all rho^2 and phi^2 values for different scenarios, including randomized and fixed values. 
        From Cardinet, Tourneur, and Allal (1976) The Symmetry of Generalizability Theory: Applications to Educational Measurement.
        
        Ep^2(alpha) = sigma^2(tau)/(sigma^2(tau) + sigma^2(delta))
        
        sigma^2(tau) = sigma^2(alpha) + sigma^2(alpha_fixed)/n_fixed, where alpha_fixed represents all interaction variances between alpha and ONLY fixed factors
        sigma^2(delta) = sigma^2(alpha_random)/n_random, where alpha_random represents all interaction variances containing alpha and random factors
        
        Args:
            variance_dict (dict): A dictionary containing the variance components. The keys represent the facets or their interactions,
            and the values are their respective variance values.
        
        Returns:
            pd.DataFrame: A DataFrame containing the G-coefficients for different scenarios with the following columns:
            - 'Source of Variation': The source of variance.
            - 'Generalized Over Random': The facets that are considered random.
            - 'Generalized Over Fixed': The facets that are considered fixed.
            - 'rho^2': The generalizability coefficient.
            - 'phi^2': The dependability coefficient.
        """
        
        g_coeff_df = pd.DataFrame(columns=['Source of Variation', 'Generalized Over Random', 'Generalized Over Fixed', 'rho^2', 'phi^2'])
        
        max_key = max([key for key in variance_dict.keys()], key=len)  # This represents the highest order interaction e.g. 'A × B × C'
        
        for key, variance in variance_dict.items():
            if key == max_key:
                continue  # The generalizability coefficient for the highest order interaction is not needed
            
            # Get the number of facets in the key
            n_facets = len(self.source_of_variance[key])
            
            # determine the number of random and fixed facets
            # Get the number of fixed facets
            max_fixed = len(self.facets) - n_facets - 1 # -1 bc one variable must always be random
            # For example, in a 3 facet design, we can only have 1 fixed facet, otherwise the generalizability scenario does not make sense
            # i.e. if we want to know if a is generalizable, we can only fix b or c, not both
            # We want to get generalizability coefficients for all possible scenarios except the scenario involving all interactions, error
            # i.e. if we have 'a x b x c', we want to exclude 'a x b x c'
            
            # The current facets in question
            variance_tup = self.source_of_variance[key]
            key_facets = list(variance_tup)
            
            # Let's get the facets that are not in the variance_tup
            potential_variable_facets = [facet for facet in self.facets if facet not in variance_tup] 
            
            # Let's get all possible combinations of fixed and randomized facets
            fixed_list = []
            randomized_list = []
            for r in range(1, len(self.facets)):
                for combo in combinations(potential_variable_facets, r):
                    if r <= max_fixed:
                        fixed_list.append(combo)
                    randomized_list.append(combo)
                    
            fixed_list.append(())  # Add a scenario where all facets are randomized
            
            # Let's assume unless specified as fixed, all other facets are randomized
            for fixed in fixed_list:
                randomized = [facet for facet in potential_variable_facets if facet not in fixed]
                sigma_squared_tau = variance  # The variance of the facet in question
                # First we need to get any lower order interactions that contain the facet(s) in question
                tau_list = [] 
                for r in range(1, len(variance_tup)):
                    for combo in combinations(variance_tup, r):
                        tau_list.append(combo)
                        sigma_squared_tau += variance_dict[' × '.join(combo)]
                        
                # Next we need to get any higher order interactions between the facet(s) in question and the fixed facets
                tau_combos = list(variance_tup) + list(fixed)
                
                # reorder the tau_combos to match the order of self.facets tuple
                tau_combos = [facet for facet in self.facets if facet in tau_combos]
                
                # Capture all the higher order interactions that contain the facet(s) in question
                for r in range(len(variance_tup) + 1, len(tau_combos) + 1):
                    for combo in combinations(tau_combos, r):
                        # check if any of the facets in the combo are in key_facets 
                        # i.e. the interaction contains all the facets in the variance_tup
                        if any([facet in key_facets for facet in combo]):
                            # get the product of the levels of any fixed facets in the combo
                            pi_star = 1
                            for facet in combo:
                                if facet in fixed:
                                    pi_star *= len(self.levels[facet])
                            tau_list.append(combo)
                            sigma_squared_tau += variance_dict[' × '.join(combo)] / pi_star
                        
                
                tau_list.append(variance_tup)  # Add the main effect
                
                # RULE 4.1.3 (Brennan 2001)
                # variance(dirac_delta) is sum of all variance(alpha_bar)
                # such that alpha_bar inlcudes tau and at least one other index
                
                # For delta, we consider all possible interactions that are at the same level of interaction and contain at least one of the facets in question
                dirac_delta_list = self.source_of_variance.values()
                dirac_delta_list = [interaction for interaction in dirac_delta_list if type(interaction) is tuple and len(interaction) >= len(variance_tup) and interaction not in tau_list]

                sigma_squared_dirac_delta = 0
                
                for interaction in dirac_delta_list:
                    # check if any of the facets in the combo are in key_facets
                    if any([facet in key_facets for facet in interaction]):
                        # print(f"DIRAC DELTA Variance Combo: {' × '.join(interaction)}")
                        # print(f"Variance: {variance_dict[' × '.join(interaction)]}")
                        # get the product of the levels of any random facets in the combo
                        pi_star = 1
                        for facet in interaction:
                            if facet not in variance_tup:
                                pi_star *= len(self.levels[facet])
                        sigma_squared_dirac_delta += variance_dict[' × '.join(interaction)] / pi_star
                        
                # RULE 4.1.2 (Brennan 2001)
                # variance(delta) is the sum of all variance(alpha_bar) except variance(tau)
                delta_list = self.source_of_variance.values()
                delta_list = [interaction for interaction in delta_list if type(interaction) is tuple and interaction not in tau_list]
                
                sigma_squared_delta = 0
                
                for interaction in delta_list:
                    # print(f"DELTA Variance Combo: {' × '.join(interaction)}")
                    # print(f"Variance: {variance_dict[' × '.join(interaction)]}")
                    # get the product of the levels of any random facets in the combo
                    pi_star = 1
                    for facet in interaction:
                        if facet not in variance_tup:
                            pi_star *= len(self.levels[facet])
                    sigma_squared_delta += variance_dict[' × '.join(interaction)] / pi_star
                
                
                # Get the G-coefficient
                g_coefficient = sigma_squared_tau / (sigma_squared_tau + sigma_squared_dirac_delta + 1e-8)  # Add a small value to avoid division by zero
                
                # Get the Dependability Coefficient
                dependability_coefficient = sigma_squared_tau / (sigma_squared_tau + sigma_squared_delta + 1e-8)  # Add a small value to avoid division by zero
                
                new_row = pd.DataFrame([{
                    'Source of Variation': ' × '.join(variance_tup),
                    'Generalized Over Random': ' × '.join(randomized),
                    'Generalized Over Fixed': ' × '.join(fixed) if fixed else '---',
                    'rho^2': g_coefficient, 
                    'phi^2': dependability_coefficient
                }])
                
                # Ensure dtypes match before concatenation
                new_row = new_row.astype(g_coeff_df.dtypes.to_dict())
                
                g_coeff_df = pd.concat([g_coeff_df, new_row], ignore_index=True)
                
        
        return g_coeff_df
        
    def g_coeffs(self, **kwargs):
        """
        Calculate G-coefficients for various scenarios of fixed and random facets.
        This method creates a table of all rho^2 and phi^2 values for each potential scenario of fixed and random facets for every main and interaction effect. The G-coefficients are stored in `self.g_coeff_table`.
        Parameters:
        -----------
        **kwargs : dict, optional
            Optional keyword arguments.
            - variance_dictionary (dict): A dictionary containing variance components. If provided, this dictionary will be used instead of the ANOVA table.
        Raises:
        -------
        ValueError:
            - If a variance component key from the provided dictionary is not found in the source of variance.
            - If the ANOVA table is empty and no variance dictionary is provided.
            - If the 'Total' key exists in the variance dictionary, it will be removed.
            - If any variance component is negative, it will be clipped to 0 and a warning will be printed.
        Notes:
        ------
        - If 'variance_dictionary' is provided in kwargs, it will be used as the source of variance components.
        - If 'variance_dictionary' is not provided, the method will use the ANOVA table to create the variance dictionary.
        - The method replaces ' x ' with ' × ' in the keys of the variance dictionary for consistency.
        - The method ensures that all variance components are non-negative by clipping any negative values to 0.
        - The resulting G-coefficients are stored in `self.g_coeff_table` using the `g_coeff_general` method.
        """
        if 'variance_dictionary' in kwargs:
            variance_dict = kwargs['variance_dictionary']
            print("Using User Provided Variance Dictionary")
            for key in variance_dict.keys():
                # replace 'x' with '×' in the keys
                if ' x ' in key:
                    print(f"Replacing ' x ' with ' × ' in the key: {key}")
                    variance_dict[key.replace(' x ', ' × ')] = variance_dict.pop(key)
                if key not in self.source_of_variance.keys():
                    raise ValueError(f"Variance component '{key}' not found in the source of variance. Please check the variance dictionary and try again.")
        else:
            if not self.anova_table.empty:
                variance_dict = self.anova_table.set_index('Source of Variation')['Variance Component'].to_dict()
            else:
                raise ValueError("Please calculate the ANOVA table using the calculate_anova method before calculating the G-coefficients.")
        
        # Drop 'Total' from the dictionary if it exists
        if 'Total' in variance_dict:
            variance_dict.pop('Total')
        
        # Clip any variance components that are negative to 0
        for key, value in variance_dict.items():
            if value < 0:
                variance_dict[key] = 0
                print(f"Warning: Variance component for '{key}' was negative and has been clipped to 0.")

        # Store the G-coefficients in a table
        self.g_coeff_table = self.g_coeff_general(variance_dict)
    
    # ----------------- D STUDY -----------------
    def calculate_d_study(self, levels: dict, **kwargs):
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
        
        for key in levels.keys():
            if key not in self.facets:
                raise ValueError(f"Facet {key} not found in the design. Please Update the levels dictionary to include only valid facets.")
            if levels[key] is None:
                levels[key] = [len(self.levels[key])]
                print(f"Levels for {key} not provided. Keeping the levels the same as the original design.")
                
        # Check that the levels dictionary contains list of integer values greater than 0
        for key, value in levels.items():
            if not isinstance(value, list) and value is not None:
                raise ValueError(f"Levels for facet {key} must be a list of integers or `None`. Please check the levels dictionary and try again.")
            if value is not None:
                if any([not isinstance(val, int) for val in value]):
                    raise ValueError(f"All levels for facet {key} must be integers. Please check the levels dictionary and try again.")
                if any([val <= 0 for val in value]):
                    raise ValueError(f"All levels for facet {key} must be greater than 0. Please check the levels dictionary and try again.")
        
        # Check to make sure all facets are accounted for
        if len(levels.keys()) != len(self.facets):
            # Get the missing facets
            missing_facets = [facet for facet in self.facets if facet not in levels.keys()]
            
            # Add the missing facets to the levels dictionary
            for facet in missing_facets:
                print(f"Facet {facet} not found in the levels dictionary. Keeping the levels the same as the original design.")
                levels[facet] = [len(self.levels[facet])]
                
        
        og_levels = copy.deepcopy(self.levels) # Store the original levels
        
        # Create a list of tuples containing all possible combinations of levels
        level_combinations = list(product(*levels.values()))
        
        self.d_study_table = pd.DataFrame()
        
        if 'variance_dictionary' in kwargs:
            print("Using User Provided Variance Dictionary for D-Study")
            variance_dict = kwargs['variance_dictionary']
            for key in variance_dict.keys():
                # replace 'x' with '×' in the keys
                if ' x ' in key:
                    print(f"Replacing ' x ' with ' × ' in the key: {key}")
                    variance_dict[key.replace(' x ', ' × ')] = variance_dict.pop(key)
                if key not in self.source_of_variance.keys():
                    raise ValueError(f"Variance component '{key}' not found in the source of variance. Please check the variance dictionary and try again.")
            # Check if 'Total' is in the dictionary and remove it
            if 'Total' in variance_dict:
                variance_dict.pop('Total')
        else:
            print("Using ANOVA Table Variance Dictionary for D-Study")
            variance_dict = self.anova_table.set_index('Source of Variation')['Variance Component'].to_dict()
            # Drop 'Total' from the dictionary
            variance_dict.pop('Total')
        
        # Clip any variance components that are negative to 0
        variance_dict = {key: max(0, value) for key, value in variance_dict.items()}
        
        for combo in level_combinations:
            for i, key in enumerate(levels.keys()):
                if len(self.levels[key]) < combo[i]:
                    # Add numbers j from len(self.levels[key]) to combo[i]
                    for j in range(len(self.levels[key]) + 1, combo[i] + 1):
                        self.levels[key] = np.append(self.levels[key], j)
                else:
                    self.levels[key] = self.levels[key][:combo[i]]
            
            # calculate the generalizability coefficients
            d_coeffs = self.g_coeff_general(variance_dict)
            
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
            
        Returns:
            self.confidence_intervals (dict): A dictionary containing the 95% confidence intervals for each level of each facet.
        """
        # Check if the ANOVA table has been calculated
        if self.anova_table.empty:
            raise ValueError("Please calculate the ANOVA table using the calculate_anova method before calculating the confidence intervals.")
        
        
        self.confidence_intervals = {}
        
        var_table = self.anova_table.set_index('Source of Variation')['Variance Component'].to_dict()
        
        # Drop 'Total' from the dictionary
        var_table.pop('Total')
        
        # Clip any variance components that are negative to 0
        for key, value in var_table.items():
            if value < 0:
                print(f"Warning: Variance component for '{key}' was negative and has been clipped to 0.")
                var_table[key] = 0
        
        for key in var_table.keys():
            if ':' in key or ' × ' in key:
                continue  # Skip interaction effects
            
            # Sum the variances all other variances divided by the product of the levels of the other facets
            # Do not include the variance of the facet in question or the level of the facet in question
            # For example, sigma^2(aBC) = sigma^2(b)/n_b + sigma^2(c)/n_c + sigma^2(bc)/n_b*n_c + sigma^2(ab)/n_b + sigma^2(ac)/n_c + sigma^2(abc)/n_b*n_c*n_a
            sigma_squared = 0
            for var in var_table.keys():
                if var == key:
                    continue
                pi_star = 1
                if len(self.source_of_variance[var]) == 1:
                    # This is a main effect
                    pi_star = len(self.levels[var])
                else:
                    # This is an interaction effect
                    # split the interaction into its components
                    facets = var.split(' × ')
                    for facet in facets:
                        pi_star *= len(self.levels[facet])
                
                sigma_squared += var_table[var] / pi_star
            
            # Use the alpha value to get the z_alpha/2 value
            z_alpha = norm.ppf(1 - alpha/2)
            interval = z_alpha * np.sqrt(sigma_squared)

            # Get the means and unique values of the responses for the key
            means = self.data.groupby(key)[self.response].mean().values
            unique_values = self.levels[key]
            self.confidence_intervals[key] = {val: (m - interval, m, m + interval) for val, m in zip(unique_values, means)}
            
            
    # ----------------- Summary Tables -----------------
    def d_study_summary(self):
        """
        Print a summary of the D-Study results.
        """
        
        # Identify unique combinations of levels (facet values) dynamically using self.facets
        unique_combinations = self.d_study_table[list(self.facets)].drop_duplicates()

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
        
        



# if __name__ == "__main__":
#     # ---------------------------------------------------------
#     # SYNTHETIC DATA FROM BRENNAN (2001) - SYTNHETIC DATA SET NO. 3

#     data = {
#         'Person': range(1, 11),
#         'O1_i1': [2, 4, 5, 5, 4, 4, 2, 3, 0, 6],
#         'O1_i2': [6, 5, 5, 9, 3, 4, 6, 4, 5, 8],
#         'O1_i3': [7, 6, 4, 8, 5, 4, 6, 4, 4, 7],
#         'O1_i4': [5, 7, 6, 6, 6, 7, 5, 5, 5, 6],
#         'O2_i1': [2, 6, 5, 5, 4, 6, 2, 6, 5, 6],
#         'O2_i2': [5, 7, 4, 7, 5, 4, 7, 6, 5, 8],
#         'O2_i3': [5, 5, 5, 7, 6, 7, 7, 6, 5, 8],
#         'O2_i4': [5, 7, 5, 6, 4, 8, 5, 4, 3, 6]
#     }

#     # Create a DataFrame
#     df = pd.DataFrame(data)

#     print(df.head(10))

#     # New DataFrame with 'Person', 'i', 'o', and 'Response'
#     new_data = {
#         'Person': [],
#         'i': [],
#         'o': [],
#         'Response': []
#     }

#     # Populate the new DataFrame
#     for person in range(1, 11):
#         for o in [1, 2]:  # Assuming 'O1' and 'O2'
#             for i in range(1, 5):  # Assuming 'i1', 'i2', 'i3', 'i4'
#                 key = f'O{o}_i{i}'
#                 response = df.at[person-1, key]
#                 new_data['Person'].append(person)
#                 new_data['i'].append(i)
#                 new_data['o'].append(o)
#                 new_data['Response'].append(response)

#     # Convert to DataFrame
#     formatted_df = pd.DataFrame(new_data)

#     print(formatted_df.head(8))
#     print(formatted_df.tail(8))
    
#     GT = DesignCrossed(formatted_df)
    
#     GT.calculate_anova()
#     GT.g_coeff()
    
#     GT.anova_summary()
#     GT.g_coeff_summary()


    # GT = GeneralizIT(formatted_df, ['Person', 'i', 'o'], 'Response')
    # GT.calculate_anova()

    # # Differentiation table for different rho^2 and phi scenarios
    # GT.g_coeffs()

    # # Perform a D-Study
    # GT.d_study(levels = {
    #                 'Person': None,
    #                 'i': [4, 8],
    #                 'o': [1, 2]
    #             })

    # # Get the confidence intervals for each facet's mean scores
    # GT.confidence_intervals()

    # # # Summary Statistics
    # GT.anova_summary()  # Print ANOVA table
    # GT.variance_summary()  # Print only the variance components
    # GT.g_coeff_summary()  # Print differentiation table
    # GT.d_study_summary()  # Print D-Study results
    # GT.confidence_interval_summary()  # Print confidence intervals
    # ---------------------------------------------------------