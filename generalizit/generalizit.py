import re
from typing import Tuple, Optional, Dict, List
import numpy as np
import pandas as pd
from generalizit.design import Design
from generalizit.design_utils import parse_facets, match_research_design, validate_research_design, get_facets_from_variance_tuple_dictionary
import warnings

class GeneralizIT:
    """
    High-level API for Generalizability Theory analysis.
    
    GeneralizIT provides a user-friendly interface for conducting Generalizability Theory (G-Theory) 
    analyses, including variance component estimation, reliability coefficient calculation,
    Decision studies (D-studies), and confidence interval estimation.
    
    This class serves as a wrapper around the core analytical engine (Design class),
    handling data preparation, research design interpretation, and result presentation.
    
    Parameters:
        data (pd.DataFrame): Dataset containing facet variables and response measurements.
        design_str (str): String specifying the research design in standard notation 
                        (e.g., "p x i" for persons crossed with items).
        response (str): Column name in data containing the response/measurement values.
        
    Attributes:
        design (Design): The underlying Design object that performs calculations.
        
    Example:
        >>> import pandas as pd
        >>> from generalizit import GeneralizIT
        >>> data = pd.read_csv("my_data.csv")
        >>> gt = GeneralizIT(data, "p x i", "score")
        >>> gt.calculate_anova()
        >>> gt.calculate_g_coefficients()
        >>> gt.g_coefficients_summary()
    """
    def __init__(self, data: pd.DataFrame, design_str: str, response: str, variance_tuple_dictionary: Optional[Dict[str, Tuple[str, ...]]] = None):
        # Initialize the GeneralizIT class

        # If a variance tuple dictionary is not provided, create one
        if variance_tuple_dictionary is None:
            # First we parse the input string to get the research design
            design_num, facets = match_research_design(design_str)
            
            # Validate the research design
            try:
                validate_research_design(design_num)
            except ValueError as e:
                raise ValueError(e)
            
            variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)
        else:
            # Validate the provided variance tuple dictionary
            if not isinstance(variance_tuple_dictionary, dict):
                raise ValueError("variance_tuple_dictionary must be a dictionary.")
            if not all(isinstance(k, str) and isinstance(v, tuple) for k, v in variance_tuple_dictionary.items()):
                raise ValueError("variance_tuple_dictionary must contain string keys and tuple values.")
            facets = get_facets_from_variance_tuple_dictionary(variance_tuple_dictionary)

        data, missing_data = self._clean_data(data=data, facets=facets, response=response)

        # Initialize the design class based on the research design
        self.design = Design(
            data=data,
            variance_tuple_dictionary=variance_tuple_dictionary,
            missing_data=missing_data,
            response_col=response
        )
            
    def _clean_data(self, data: pd.DataFrame, facets: list[str], response: str) -> Tuple[pd.DataFrame, bool]:
        """
        Prunes the input DataFrame by dropping columns that are not in the list of facets or the response variable. 

        Args:
            data (pd.DataFrame): The input DataFrame to be pruned.
            facets (list[str]): The list of facet column names.
            response (str): The response variable column name.

        Returns:
            pd.DataFrame: The pruned DataFrame containing only the columns specified in facets and the response variable.
            bool: A boolean indicating whether there are missing values in the data.
        """
        for col in data.columns:
            if col != response:
                data = data.rename(columns={col: re.sub(r"\s+", " ", col.strip().lower())})  # Normalize the column names
        
        # Combine factors and response variable into a single list
        variables = list(facets) + [response]
        # Create a list of columns to drop
        drop_cols = [col for col in data.columns if col not in variables]
        
        # Create a warning message if any columns are dropped
        if len(drop_cols) > 0:
            print("Warning: The following columns have been dropped from the data:")
            for col in drop_cols:
                print(col)
        
        # Drop the columns
        data = data.drop(columns=drop_cols)

        # Check for missing values
        if data.isnull().values.any():
            print("Warning: Missing values detected in the data.")
            missing_data = True
        else:
            missing_data = False

        return data, missing_data
    
    def calculate_anova(self):
        """
        Calculate variance components using ANOVA.
        
        This method is a wrapper for the Design.calculate_anova() method, which
        implements Henderson's Method 1 to estimate variance components for each facet
        in the specified research design.
        
        Returns:
            None: Results are stored in the underlying Design object.
            
        Notes:
            This method must be called before calculating G-coefficients,
            confidence intervals, or D-study scenarios.
        """
        # Calculate the ANOVA table
        self.design.calculate_anova()
    
    def calculate_g_coefficients(self, fixed_facets: Optional[List[str]] = None, **kwargs):
        """
        Calculate generalizability coefficients.
        
        This method is a wrapper for the Design.g_coeffs() method, which computes 
        phi-squared (Φ²) and rho-squared (ρ²) coefficients for each potential
        object of measurement in the design.
        
        Parameters:
            - fixed_facets Optional(List[str]): List of facets to be treated as fixed.
            **kwargs: Optional keyword arguments passed to Design.g_coeffs().
                - error_variance (bool): If True, prints detailed information about
                  error variances during calculation. Default is False.
                - Other parameters as documented in Design.g_coeffs().
                
        Returns:
            None: Results are stored in the underlying Design object.
            
        Raises:
            RuntimeError: If ANOVA table hasn't been calculated first.
        """
        # First check that the ANOVA table has been calculated
        if self.design.anova_table is None:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
        
        # Check that the fixed facets are valid
        if fixed_facets is not None:
            if not isinstance(fixed_facets, list):
                raise ValueError("fixed_facets must be a list.")
            max_tuple = max(self.design.variance_tuple_dictionary.values(), key=len)
            if len(fixed_facets) > len(max_tuple) - 2:
                raise ValueError("The number of fixed facets cannot exceed the number of facets in the design minus 2.")
            all_facets = set(f for t in self.design.variance_tuple_dictionary.values() for f in t)
            for facet in fixed_facets:
                if facet not in all_facets:
                    raise ValueError(f"Fixed facet '{facet}' not found in the design facets: {all_facets}")
            print("Warning: Fixed facets should only be used with balanced designs without missing data.")
                
        # Calculate the G coefficients
        self.design.g_coeffs(fixed_facets=fixed_facets, **kwargs)
        
    def g_coeffs(self, **kwargs):
        """
        [DEPRECATED] Calculate generalizability coefficients.
        
        This method is deprecated and will be removed in a future version.
        Please use `calculate_g_coefficients()` instead.
        
        See `calculate_g_coefficients()` for parameter details.
        """
        warnings.warn(
            "The g_coeffs() method is deprecated and will be removed in a future version. "
            "Please use calculate_g_coefficients() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.calculate_g_coefficients(**kwargs)
        
    def calculate_d_study(self, d_study_design: Optional[dict] = None, fixed_facets: Optional[List[str]] = None, **kwargs):
        """
        Calculate G-coefficients for alternative research designs (D-Study).
        
        This method is a wrapper for the Design.calculate_d_study() method, which examines
        multiple possible study designs by generating combinations of provided facet levels.
        
        Parameters:
            - d_study_design (dict, optional): Dictionary where keys are facet names and values are 
                lists of integers representing different numbers of levels to test.
            - fixed_facets Optional(List[str]): List of facets to be treated as fixed.
            - **kwargs: Optional keyword arguments passed to Design.calculate_d_study().
                
        Returns:
            None: Results are stored in the underlying Design object.
            
        Raises:
            RuntimeError: If ANOVA table hasn't been calculated first.
        """
        # First check that the ANOVA table has been calculated
        if self.design.anova_table.empty:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
        
        # Check that the fixed facets are valid
        if fixed_facets is not None:
            if not isinstance(fixed_facets, list):
                raise ValueError("fixed_facets must be a list.")
            max_tuple = max(self.design.variance_tuple_dictionary.values(), key=len)
            if len(fixed_facets) > len(max_tuple) - 2:
                raise ValueError("The number of fixed facets cannot exceed the number of facets in the design minus 2.")
            all_facets = set(f for t in self.design.variance_tuple_dictionary.values() for f in t)
            for facet in fixed_facets:
                if facet not in all_facets:
                    raise ValueError(f"Fixed facet '{facet}' not found in the design facets: {all_facets}")
            print("Warning: Fixed facets should only be used with balanced designs without missing data.")
        
        # Calculate the D study
        self.design.calculate_d_study(d_study_design=d_study_design, fixed_facets=fixed_facets, **kwargs)
        
    def calculate_confidence_intervals(self, alpha: float = 0.05, **kwargs):
        """
        Calculate confidence intervals for facet level means.
        
        This method is a wrapper for the Design.calculate_confidence_intervals() method,
        which computes confidence intervals for individual facets based on variance 
        component analysis.
        
        Parameters:
            alpha (float, optional): Significance level for confidence intervals.
                Default is 0.05 (producing 95% confidence intervals).
            **kwargs: Optional keyword arguments passed to Design.calculate_confidence_intervals().
                
        Returns:
            None: Results are stored in the underlying Design object.
            
        Raises:
            RuntimeError: If ANOVA table hasn't been calculated first.
        """
        # First check that the ANOVA table has been calculated
        if self.design.anova_table.empty:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
            
        # Calculate the confidence intervals
        self.design.calculate_confidence_intervals(alpha=alpha, **kwargs)
        
    # ----------------- Summary Methods -----------------  
    def anova_summary(self):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table.empty:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
        
        # Print the ANOVA table
        self.design.anova_summary()

    def variance_summary(self):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table.empty:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")

        # Print the variance components
        self.design.variance_summary()
    
    def g_coefficients_summary(self):
        # First check that the G coefficients have been calculated
        if self.design.g_coeffs_table.empty:
            raise RuntimeError("G coefficients must be calculated first. Please run the g_coeffs() method.")
        
        # Print the G coefficients
        self.design.g_coeff_summary()

    def d_study_summary(self):
        # First check that the D study has been calculated
        if not self.design.d_study_dict:
            raise RuntimeError("D study must be calculated first. Please run the calculate_d_study() method.")
        
        # Print the D study
        self.design.d_study_summary()
        
    def confidence_intervals_summary(self):
        # First check that the confidence intervals have been calculated
        if self.design.confidence_intervals is {}:
            raise RuntimeError("Confidence intervals must be calculated first. Please run the calculate_confidence_intervals() method.")
        
        # Print the confidence intervals
        self.design.confidence_intervals_summary()
# ---- End of GeneralizIT Class ----

# # ---- Wrapper Documentation ----
# GeneralizIT.calculate_anova.__doc__ = (
#     GeneralizIT.calculate_anova.__doc__ + 
#     "\n\n" + 
#     Design.anova_summary.__doc__
# )
# GeneralizIT.calculate_g_coefficients.__doc__ = (
#     GeneralizIT.calculate_g_coefficients.__doc__ + 
#     "\n\n" + 
#     Design.g_coeffs.__doc__
# )
# GeneralizIT.calculate_d_study.__doc__ = (
#     GeneralizIT.calculate_d_study.__doc__ + 
#     "\n\n" + 
#     Design.calculate_d_study.__doc__
# )
# GeneralizIT.calculate_confidence_intervals.__doc__ = (
#     GeneralizIT.calculate_confidence_intervals.__doc__ + 
#     "\n\n" + 
#     Design.calculate_confidence_intervals.__doc__
# )
# GeneralizIT.anova_summary.__doc__ = Design.anova_summary.__doc__
# GeneralizIT.variance_summary.__doc__ = Design.variance_summary.__doc__
# GeneralizIT.g_coefficients_summary.__doc__ = Design.g_coeff_summary.__doc__
# GeneralizIT.d_study_summary.__doc__ = Design.d_study_summary.__doc__
# GeneralizIT.confidence_intervals_summary.__doc__ = Design.confidence_intervals_summary.__doc__
# # ---- End of Wrapper Documentation ----
