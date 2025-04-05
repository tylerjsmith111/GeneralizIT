import pandas as pd
import itertools

def create_pseudo_df(d_study: dict, variance_tup_dict: dict) -> pd.DataFrame:
    """
    Create a pseudo DataFrame with all possible combinations of facet levels.

    Parameters:
        d_study (dict): A dictionary representing the study design with facets as keys and 
                        the number of levels for each facet as values.
        variance_tup_dict (dict): A dictionary mapping facet names to tuples containing the 
                                 component facets.

    Returns:
        pd.DataFrame: A pseudo DataFrame with all possible combinations of facet levels.
    """
    # Identify independent variables (facets without ":" or " x ")
    independent_vars = [var for var in variance_tup_dict.keys() if ":" not in var and " x " not in var]
    
    # Debugging: Print the unnested variables
    # print(f"Variance Tuple Dictionary: {variance_tup_dict}")
    # print(f"Unnested Variables: {independent_vars}")
    
    
    # Identify dependent variables and their dependencies
    dependent_vars = {}
    for comp_name, components in variance_tup_dict.items():
        if ":" in comp_name and " x " not in comp_name:
            dependent_var = components[0]  # The first component is typically the dependent variable
            dependencies = components[1:]  # The rest are the variables it depends on
            dependent_vars[dependent_var] = dependencies
    
    # Generate all possible combinations of independent variable levels
    independent_levels = {var: list(range(1, d_study[var] + 1)) for var in independent_vars}
    independent_combinations = list(itertools.product(*[independent_levels[var] for var in independent_vars]))
    
    # Initialize the data dictionary for the DataFrame
    data = {facet: [] for facet in d_study.keys()}
    
    # Generate rows for the DataFrame
    for combo in independent_combinations:
        # Map each value to its independent variable
        ind_var_values = dict(zip(independent_vars, combo))
        
        # For dependent variables, generate all possible levels for each combo of independent variables
        dep_var_combinations = []
        for dep_var, deps in dependent_vars.items():
            # Get all relevant independent variable values for this dependent variable
            relevant_ind_vars = [ind_var_values[var] for var in deps if var in ind_var_values]
            
            # If the dependent variable depends on independent variables we have values for
            if len(relevant_ind_vars) == len(deps):
                # Generate all levels for this dependent variable
                dep_levels = list(range(1, d_study[dep_var] + 1))
                dep_var_combinations.append([(dep_var, level) for level in dep_levels])
            else:
                # Skip this dependent variable if dependencies not met
                continue
        
        # Generate all combinations of dependent variable levels
        if dep_var_combinations:
            for dep_combo in itertools.product(*dep_var_combinations):
                # Create a row with independent variable values
                row_values = ind_var_values.copy()
                
                # Add dependent variable values
                for dep_var, level in dep_combo:
                    row_values[dep_var] = level
                
                # Add this row to the data dictionary
                for facet, value in row_values.items():
                    data[facet].append(value)
        else:
            # If no dependent variables, just add the independent variable values
            for facet, value in ind_var_values.items():
                data[facet].append(value)
    
    return pd.DataFrame(data)