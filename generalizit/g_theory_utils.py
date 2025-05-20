import pandas as pd
from typing import Dict, Union, List, Tuple, Any, Optional
import itertools
from itertools import combinations

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
            
    # print(f"Top level facets: {ordered_facets}")
    
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

    # print(f"Ordered facets after processing: {ordered_facets}")
    # Reverse the order for proper nesting in for loops
    # In a design like i:p, we want loops ordered as p then i
    ordered_facets.reverse()
    
    # print(f"Ordered facets for nested structure: {ordered_facets}")
    
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


def adjust_for_fixed_effects(
    variance_tup_dict: Dict[str, tuple], 
    variance_df: pd.DataFrame, 
    levels_df: pd.DataFrame, 
    fixed_facets: Optional[List[str]],
    verbose: bool = False
) -> Tuple[Dict[str, tuple], pd.DataFrame]:
    
    """
    Adjust variance components for fixed facets in any design.
    Follows Brennan's rule 4.3.1: For every alpha, absorb any variance component with alpha and fixed facet into the lower-order component.
    Args:
        variance_tup_dict: dict mapping component names to tuples of facets.
        variance_df: DataFrame with index as variance component names and a 'Variance' column.
        levels_df: DataFrame of levels coefficients (1/levels).
        fixed_facets: list of facets to fix (e.g., ['i']).
        verbose: bool, if True, print debug information.
    Returns:
        adjusted_variance_tup_dict: dict mapping adjusted component names to tuples of facets.
        adjusted_variance_df: DataFrame with adjusted variance components.
    """
    def vprint(*args, **kwargs):
        """Verbose print function."""
        if verbose:
            print(*args, **kwargs)
            
    if fixed_facets is None:
        vprint("No fixed facets provided. Returning original variance components.")
        return variance_tup_dict, variance_df
    else:
        # Gather all unique facets
        all_facets = set()
        for facets in variance_tup_dict.values():
            all_facets.update(facets)
        all_facets = list(all_facets)
        vprint(f"All facets: {all_facets}")

        # Identify random facets
        random_facets = [facet for facet in all_facets if facet not in fixed_facets]
        vprint(f"Random facets: {random_facets}")

        # Prepare variance dict
        adjusted_variance_dict = variance_df['Variance'].to_dict()
        adjusted_variance_dict.pop('mean', None)
        vprint(f"Initial variance dict: {adjusted_variance_dict}")

        # Remove fixed facet main effects
        for fixed_facet in fixed_facets:
            adjusted_variance_dict.pop(fixed_facet, None)
        vprint(f"Variance dict after removing fixed facets: {adjusted_variance_dict}")

        # Only keep keys not involving fixed facets
        key_list = [
            key for key in adjusted_variance_dict
            if not any(facet in variance_tup_dict[key] for facet in fixed_facets)
        ]
        vprint(f"Keys to keep: {key_list}")

        # Absorb higher-order interactions with fixed facets
        for variance in key_list:
            facets = list(variance_tup_dict[variance])
            initial_var = adjusted_variance_dict[variance]
            combinations_list = facets + list(fixed_facets)
            interaction_tuples = []
            for r in range(len(facets) + 1, len(combinations_list) + 1):
                for combo in combinations(combinations_list, r):
                    interaction_tuples.append(combo)
            vprint(f"Interactions for {variance}: {interaction_tuples}")

            for interaction in interaction_tuples:
                for key, tup in variance_tup_dict.items():
                    if set(interaction) == set(tup) and key in adjusted_variance_dict:
                        vprint(f"Absorbing {key} into {variance}")
                        initial_var += adjusted_variance_dict[key] * levels_df.at[variance, key]
                        adjusted_variance_dict[key] = None  # Mark for removal
                        break
            adjusted_variance_dict[variance] = round(initial_var, 4)

        # Remove absorbed keys
        adjusted_variance_dict = {k: v for k, v in adjusted_variance_dict.items() if v is not None}
        vprint(f"Final adjusted variance dict: {adjusted_variance_dict}")

        # Build adjusted tuple dict and DataFrame
        adjusted_variance_tup_dict = {k: variance_tup_dict[k] for k in adjusted_variance_dict}
        adjusted_variance_df = pd.DataFrame.from_dict(adjusted_variance_dict, orient='index', columns=['Variance'])

        return adjusted_variance_tup_dict, adjusted_variance_df