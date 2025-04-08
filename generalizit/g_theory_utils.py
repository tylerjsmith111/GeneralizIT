import pandas as pd
from typing import Dict, Union, List, Tuple, Any
import itertools

def create_pseudo_df(d_study: Dict[str, int], variance_tup_dict: Dict[str, tuple]) -> pd.DataFrame:
    """
    Create a pseudo DataFrame with all possible combinations of facet levels.

    Parameters:
        d_study (dict): A dictionary representing the study design with facets as keys and 
                        the number of levels for each facet as values. Values can be either
                        integers or lists of integers.
        variance_tup_dict (dict): A dictionary mapping facet names to tuples containing the 
                                 component facets.

    Returns:
        pd.DataFrame: A pseudo DataFrame with all possible combinations of facet levels.
    """    
    # Identify nested structure from variance_tup_dict
    nested_vars = {}
    crossed_vars = set()
    
    for comp_name, components in variance_tup_dict.items():
        if ":" in comp_name and " x " not in comp_name:
            # This is a nested relationship
            # For a string like "i:p", components would be ("i", "p")
            # where i is nested within p
            nested_relationship = list(components)
            for i in range(len(nested_relationship) - 1):
                child = nested_relationship[i]
                parent = nested_relationship[i + 1]
                if child not in nested_vars:
                    nested_vars[child] = []
                nested_vars[child].append(parent)
        elif " x " in comp_name:
            # This is a crossed relationship
            for component in components:
                crossed_vars.add(component)
    
    # Find all facets
    all_facets = set(d_study.keys())
    
    # Order facets based on nesting
    ordered_facets = []
    
    # First add facets that are not nested within anything (top level)
    for facet in all_facets:
        if facet not in nested_vars:
            ordered_facets.append(facet)
            
    print(f"Top level facets: {ordered_facets}")
    
    # Then add nested facets in order of nesting depth
    remaining_facets = all_facets - set(ordered_facets)
    while remaining_facets:
        for facet in list(remaining_facets):
            # If all parents of this facet are already in ordered_facets
            if facet in nested_vars and all(parent in ordered_facets for parent in nested_vars[facet]):
                ordered_facets.append(facet)
                remaining_facets.remove(facet)
        
        # If we couldn't add any more facets, there might be a circular dependency
        if not set(ordered_facets) & remaining_facets:
            # Add remaining facets in arbitrary order
            ordered_facets.extend(list(remaining_facets))
            break

    print(f"Ordered facets after processing: {ordered_facets}")
    # Reverse the order for proper nesting in for loops
    # In a design like i:p, we want loops ordered as p then i
    ordered_facets.reverse()
    
    print(f"Ordered facets for nested structure: {ordered_facets}")
    
    # Generate all combinations
    data = {facet: [] for facet in all_facets}
    
    # Use nested loops to generate combinations
    def generate_combinations(facet_index=0, current_values={}):
        if facet_index >= len(ordered_facets):
            # We've assigned values to all facets, add to data
            for facet, value in current_values.items():
                data[facet].append(value)
            return
        
        current_facet = ordered_facets[facet_index]
        num_levels = d_study[current_facet]
        
        for level in range(1, num_levels + 1):
            new_values = current_values.copy()
            new_values[current_facet] = level
            generate_combinations(facet_index + 1, new_values)
    
    generate_combinations()
    
    # Create DataFrame
    return pd.DataFrame(data)