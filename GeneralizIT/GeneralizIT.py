import re
import numpy as np
import pandas as pd
from GeneralizIT.design2 import Design2
from GeneralizIT.design4 import Design4
from GeneralizIT.design5 import Design5
from GeneralizIT.design6 import Design6
from GeneralizIT.design7 import Design7
from GeneralizIT.design8 import Design8
from GeneralizIT.designcrossed import DesignCrossed
from GeneralizIT.design_utils import *

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
        
        # Parse the facets if the design number is not "crossed"
        if design_num != "crossed":
            corollary_df = parse_facets(design_num=design_num, design_facets=facets)
            
        # clean the data
        data = self._clean_data(data, facets, response)
            
        # Initialize the design class based on the research design
        if design_num == 2:
            self.design = Design2(data, corollary_df)
        elif design_num == 4:
            self.design = Design4(data, corollary_df)
        elif design_num == 5:
            self.design = Design5(data, corollary_df)
        elif design_num == 6:
            self.design = Design6(data, corollary_df)
        elif design_num == 7:
            self.design = Design7(data, corollary_df)
        elif design_num == 8:
            self.design = Design8(data, corollary_df)
        elif design_num == "crossed":
            self.design = DesignCrossed(data)
        else:
            raise ValueError("Invalid research design please check the input string")
            
    def _clean_data(self, data: pd.DataFrame, facets: list[str], response: str) -> pd.DataFrame:
        """
        Prunes the input DataFrame by dropping columns that are not in the list of facets or the response variable. 
        
        Sets the response variable to be 'Response' if it is not already.

        Args:
            data (pd.DataFrame): The input DataFrame to be pruned.
            facets (list[str]): The list of facet column names.
            response (str): The response variable column name.

        Returns:
            pd.DataFrame: The pruned DataFrame containing only the columns specified in facets and the response variable.
        """
        
        
        for col in data.columns:
            if col != response:
                data = data.rename(columns={col: re.sub(r"\s+", " ", col.strip().lower())})  # Normalize the column names
            else:
                # Set the response variable to 'Response'
                data = data.rename(columns={col: 'Response'})  # Rename the response variable to 'Response' for consistency
        
        # Combine factors and response variable into a single list
        vars = list(facets) + ['Response']
        
        print(vars)
        
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
    
    def calculate_anova(self):
        # Calculate the ANOVA table
        self.design.calculate_anova()
    
    def g_coeffs(self):
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
    
    def g_coeff_summary(self):
        # First check that the G coefficients have been calculated
        if self.design.g_coeff_table is None:
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

if __name__ == "__main__":
    # ---------------------------------------------------------
    # SYNTHETIC DATA FROM BRENNAN (2001) - SYTNHETIC DATA SET NO. 3

    data = {
        'Person': range(1, 11),
        'O1_i1': [2, 4, 5, 5, 4, 4, 2, 3, 0, 6],
        'O1_i2': [6, 5, 5, 9, 3, 4, 6, 4, 5, 8],
        'O1_i3': [7, 6, 4, 8, 5, 4, 6, 4, 4, 7],
        'O1_i4': [5, 7, 6, 6, 6, 7, 5, 5, 5, 6],
        'O2_i1': [2, 6, 5, 5, 4, 6, 2, 6, 5, 6],
        'O2_i2': [5, 7, 4, 7, 5, 4, 7, 6, 5, 8],
        'O2_i3': [5, 5, 5, 7, 6, 7, 7, 6, 5, 8],
        'O2_i4': [5, 7, 5, 6, 4, 8, 5, 4, 3, 6]
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    print(df.head(10))

    # New DataFrame with 'Person', 'i', 'o', and 'Response'
    new_data = {
        'Person': [],
        'i': [],
        'o': [],
        'Response': []
    }

    # Populate the new DataFrame
    for person in range(1, 11):
        for o in [1, 2]:  # Assuming 'O1' and 'O2'
            for i in range(1, 5):  # Assuming 'i1', 'i2', 'i3', 'i4'
                key = f'O{o}_i{i}'
                response = df.at[person-1, key]
                new_data['Person'].append(person)
                new_data['i'].append(i)
                new_data['o'].append(o)
                new_data['Response'].append(response)

    # Convert to DataFrame
    formatted_df = pd.DataFrame(new_data)

    print(formatted_df.head(8))
    print(formatted_df.tail(8))
    
    GT = GeneralizIT(data=formatted_df, design_str='Person x i x o', response='Response')
    
    GT.calculate_anova()
    GT.g_coeffs()
    
    GT.anova_summary()
    GT.g_coeff_summary()
    
    GT.calculate_d_study(levels={'Person': None, 'i': [4, 8], 'o': [1, 2]})
    GT.d_study_summary()
    
    GT.calculate_confidence_intervals(alpha=0.05)
    GT.confidence_intervals_summary()
    
    # # ---------------------------------------------------------
    # Synthetic Data Set No. 2 from Brennan (2001)
    
    # Load the csv file syndata2.csv
    df = pd.read_csv('syndata2.csv')

    print(df.head())

    # New DataFrame with columns 'person', 'item', 'Response'
    new_data = {
        'person': [],
        'item': [],
        'Response': []
    }

    # Populate the new DataFrame
    for person in range(1, 11):
        for item in range(1, 9):
            key = f'personi_item{item}'
            
            if key in df.columns:
                response = df.at[person-1, key]
                new_data['person'].append(person)
                new_data['item'].append((person-1)*8 + item)
                new_data['Response'].append(response)

    # Convert to DataFrame
    formatted_df = pd.DataFrame(new_data)

    print(formatted_df.head(10))

    GT = GeneralizIT(data=formatted_df, design_str='item:person', response='Response')
    
    GT.calculate_anova()
    GT.g_coeffs()
    
    GT.anova_summary()
    GT.g_coeff_summary()
    
    GT.calculate_confidence_intervals(alpha=0.05)
    GT.confidence_intervals_summary()
    
    # # ---------------------------------------------------------
    # # Synthetic Data Set No. 4 from Brennan (2001)
    # # Load the csv file syndata4.csv
    # df = pd.read_csv('syndata4.csv')

    # print(df.head())

    # # New DataFrame with columns 'person', 't', 'r', 'Response'
    # new_data = {
    #     'person': [],
    #     't': [],
    #     'r': [],
    #     'Response': []
    # }

    # # Populate the new DataFrame
    # for person in range(1, 11):
    #     for t in [1, 2, 3]:  # Assuming 't1', 't2', 't3'
    #         for r in range(1, 13):  # Assuming 'r1' to 'r12'
    #             key = f't{t}_r{r}'
    #             # check if the key exists
    #             if key in df.columns:
    #                 response = df.at[person-1, key]
    #                 new_data['person'].append(person)
    #                 new_data['t'].append(t)
    #                 new_data['r'].append(r)
    #                 new_data['Response'].append(response)

    # # Convert to DataFrame
    # formatted_df = pd.DataFrame(new_data)

    # print(formatted_df.head(10))

    # # Initialize the GeneralizIT class
    # GT = GeneralizIT(data=formatted_df, design_str='person x (r:t)', response='Response')
    
    # GT.calculate_anova()
    # GT.g_coeffs()
    
    # GT.anova_summary()
    # GT.g_coeff_summary()
    
    # GT.calculate_d_study(levels={'person': None, 't': [1, 2, 3], 'r': [12, 6, 4]})
    # GT.d_study_summary()
    
    # GT.calculate_confidence_intervals(alpha=0.05)
    # GT.confidence_intervals_summary()
        
        