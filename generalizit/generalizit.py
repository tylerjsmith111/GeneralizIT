import re
from typing import Tuple
import numpy as np
import pandas as pd
from generalizit.design import Design
from generalizit.design_utils import parse_facets, match_research_design, validate_research_design

class GeneralizIT:
    def __init__(self, data: pd.DataFrame, design_str: str, response: str):
        # Initialize the GeneralizIT class
        # First we parse the input string to get the research design
        design_num, facets = match_research_design(design_str)
        
        # Validate the research design
        try:
            validate_research_design(design_num)
        except ValueError as e:
            raise ValueError(e)

        variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)

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
        
        Sets the response variable to be 'Response' if it is not already.

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
            else:
                # Set the response variable to 'Response'
                data = data.rename(columns={col: 'Response'})  # Rename the response variable to 'Response' for consistency
        
        # Combine factors and response variable into a single list
        variables = list(facets) + ['Response']
        
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
        # Calculate the ANOVA table
        self.design.calculate_anova()
    
    def calculate_g_coefficients(self):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table is None:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
        
        # Calculate the G coefficients
        self.design.g_coeffs()
        
    def calculate_d_study(self, levels: dict):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table is None:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
        
        # Calculate the D study
        self.design.calculate_d_study(levels=levels)
        
    def calculate_confidence_intervals(self, alpha: float = 0.05):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table is None:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
            
        # Calculate the confidence intervals
        self.design.calculate_confidence_intervals(alpha=alpha)
        
        
    # ----------------- Summary Methods -----------------  
    def anova_summary(self):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table is None:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")
        
        # Print the ANOVA table
        self.design.anova_summary()

    def variance_summary(self):
        # First check that the ANOVA table has been calculated
        if self.design.anova_table is None:
            raise RuntimeError("ANOVA table must be calculated first. Please run the calculate_anova() method.")

        # Print the variance components
        self.design.variance_summary()
    
    def g_coefficients_summary(self):
        # First check that the G coefficients have been calculated
        if self.design.g_coeffs_table is None:
            raise RuntimeError("G coefficients must be calculated first. Please run the g_coeffs() method.")
        
        # Print the G coefficients
        self.design.g_coeff_summary()

    def d_study_summary(self):
        # First check that the D study has been calculated
        if self.design.d_study_table is None:
            raise RuntimeError("D study must be calculated first. Please run the calculate_d_study() method.")
        
        # Print the D study
        self.design.d_study_summary()
        
    def confidence_intervals_summary(self):
        # First check that the confidence intervals have been calculated
        if self.design.confidence_intervals is None:
            raise RuntimeError("Confidence intervals must be calculated first. Please run the calculate_confidence_intervals() method.")
        
        # Print the confidence intervals
        self.design.confidence_intervals_summary()
        
        