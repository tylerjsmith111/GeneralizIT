import re
from typing import Optional, Dict, List, Tuple, Union
from itertools import combinations
import pandas as pd


def match_research_design(input_string: str) -> Union[Tuple[str, List], Tuple[int, List], Tuple[None, List]]:
    """
    Matches a string input of a research design to one of 8 predefined designs.
    
    Parameters:
        input_string (str): The research design input as a string.
            Valid operators are 'x' for crossing and ':' for nesting.
            Some designs require parentheses to indicate grouping.
    
    Returns:
        int or str: The design number (1 to 8) that matches the input
        List: List of facets extracted from the design string
    
    Raises:
        ValueError: If the input string is invalid or malformed
        TypeError: If the input is not a string
    
    Examples:
        >>> match_research_design("persons x raters")  # Design 1
        1
        >>> match_research_design("items:persons")     # Design 2
        2
        >>> match_research_design("p x i x h")         # Design 3
        3
        >>> match_research_design("p x (i:h)")         # Design 4
        4
    """
    # Type checking
    if not isinstance(input_string, str):
        raise TypeError("Input must be a string")
    
    # Check for empty or whitespace-only input
    if not input_string.strip():
        raise ValueError("Input string cannot be empty")
        
    # Define the patterns for each design - ordered from most specific to least specific
    # The number corresponds to the table in Brennan (2001)
    designs = {
        7: r"^\(.+\s*x\s+.+\)\s*:\s*.+$",    # (i x h):p
        4: r"^.+\s*x\s*\(.+\s*:\s*.+\)$",    # p x (i:h)
        5: r"^\(.+\s*:\s*.+\)\s*x\s+.+$",    # (i:p) x h
        6: r"^.+\s*:\s*\(.+\s*x\s+.+\)$",    # i:(p x h)
        8: r"^.+\s*:\s*.+\s*:\s*.+$",        # i:h:p
        2: r"^.+\s*:\s*.+$",                 # i:p
    }
    
    # Validate characters before normalization
    valid_chars = set("abcdefghijklmnopqrstuvwxyz0123456789():x_- ")
    if not all(c.lower() in valid_chars for c in input_string if c not in "\n\t"):
        raise ValueError("Invalid characters detected. Only letters, numbers, ':', 'x', '(', ')', '_', '-' and spaces are allowed.")
    
    # Preprocess the input string to normalize spacing and casing
    try:
        normalized_input = re.sub(r"\s+", " ", input_string.strip().lower())
        if len(normalized_input) > 100:  # Reasonable length limit
            raise ValueError("Input string is too long")
    except Exception as e:
        raise ValueError(f"Error normalizing input string: {str(e)}")
        
    # Validate parentheses matching
    if normalized_input.count("(") != normalized_input.count(")"):
        raise ValueError("Mismatched parentheses")
    
    # Validate operators
    if ":" in normalized_input and " x " in normalized_input:
        if "(" not in normalized_input or ")" not in normalized_input:
            raise ValueError("Invalid input: Parentheses are required for partially crossed designs. See examples.")

    # Split on operators while preserving the operators
    def get_facets(input_str: str) -> list:
        """
        Splits input string into facets, properly handling 'x' operator vs 'x' in words.
        """
        # First split on colons
        colon_parts = input_str.split(':')
        
        all_facets = []
        for part in colon_parts:
            # For each part, split on ' x ' (space-x-space) to avoid splitting words containing 'x'
            x_parts = part.split(' x ')
            all_facets.extend(x_parts)
        
        # Remove parentheses and strip whitespace
        facets = [term.replace("(", "").replace(")", "").strip() 
                for term in all_facets]
        
        return [facet for facet in facets if facet]  # Remove empty facets
    
    # Count and validate operators
    colon_count = normalized_input.count(":")
    cross_count = normalized_input.count(" x ")
    
    if colon_count > 2:
        raise ValueError("Invalid input: More than 2 ':' operators detected.")
    elif colon_count + cross_count > 2:
        raise ValueError("Invalid input: More than 2 operators detected.")
    elif colon_count + cross_count == 0:
        raise ValueError("Invalid input: No operators detected. Must use ':' or 'x'.")
    # Check for a fully crossed design
    elif colon_count == 0 and cross_count > 0:
        print(f"Fully Crossed Design: {normalized_input}")
        return 'crossed', get_facets(normalized_input)

    # Validate no empty facets between operators
    facets = get_facets(normalized_input)
    if any(not term.strip() for term in facets):
        raise ValueError("Invalid input: Empty facets between operators")
    
    # Check each design pattern
    try:
        for design_number, pattern in designs.items():
            if re.match(pattern, normalized_input):
                return design_number, facets
    except re.error as e:
        raise ValueError(f"Error in pattern matching: {str(e)}")
    
    # If no match but input seems valid, return None
    return None, facets

def validate_research_design(design_number: Optional[int]) -> bool:
    """
    Validates if a design number is valid (1-8).
    
    Parameters:
        design_number: The design number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return isinstance(design_number, int) and 1 <= design_number <= 8 or design_number == 'crossed'

def create_corollary_dictionary(design_num: int, design_facets: list) -> Dict[str, str]:
    """
    Parse a research design string and return a dictionary mapping facet types
    (p, i, h) to their actual values based on the design pattern.
    
    Parameters:
        design_num (int): The design number
        design_facets (list): List of facets extracted from the design string
        
    Returns:
        Dict[str, str]: Dictionary mapping facet names from the research design to base design facets.
        Keys are 'p', 'i', and/or 'h'
        
    Raises:
        ValueError: If the design pattern is invalid or can't be parsed
    """
    
    # Initialize facets dictionary
    corollary_dict = {}
    
    try:
        if design_num == 'crossed':
            return {f"facet_{i+1}": facet for i, facet in enumerate(design_facets)}
        
        elif design_num == 2:  # i:p
            corollary_dict['i'] = design_facets[0]
            corollary_dict['p'] = design_facets[1]
            
        elif design_num == 8:  # i:h:p
            corollary_dict['i'] = design_facets[0]
            corollary_dict['h'] = design_facets[1]
            corollary_dict['p'] = design_facets[2]
        
        elif design_num == 6:  # i:(p x h)
            corollary_dict['i'] = design_facets[0]
            corollary_dict['p'] = design_facets[1]
            corollary_dict['h'] = design_facets[2]
            
        elif design_num == 5:  # (i:p) x h
            corollary_dict['i'] = design_facets[0]
            corollary_dict['p'] = design_facets[1]
            corollary_dict['h'] = design_facets[2]
                
        elif design_num == 4:  # p x (i:h)
            corollary_dict['p'] = design_facets[0]
            corollary_dict['i'] = design_facets[1]
            corollary_dict['h'] = design_facets[2]
            
        elif design_num == 7:  # (i x h):p
            corollary_dict['i'] = design_facets[0]
            corollary_dict['h'] = design_facets[1]
            corollary_dict['p'] = design_facets[2]
            
        # Verify all required facets are present
        required_facets = ['i', 'p']
        if design_num >= 3:  # Designs 3-8 require all three facets
            required_facets.append('h')
            
        missing_facets = [f for f in required_facets if f not in corollary_dict]
        if missing_facets:
            raise ValueError(f"Missing required facets: {missing_facets}")
            
    except Exception as e:
        raise ValueError(f"Error parsing facets: {str(e)}")
        
    return corollary_dict


def create_variance_tuple_dictionary(
        design_num: Union[int, str],
        corollary_dict: Dict[str, str]
) -> Dict[str, tuple]:
    """
        Create a variance tuple dictionary for a given study design structure.

        This function constructs a dictionary representing variance components for a
        given study design, for example Brennan Design 2 `(i:p)`,
        where `p` and `i` represent facets of variation. The dictionary maps each
        variance component to a tuple of relevant facets.

        Parameters:
            design_num (int): The design number (2,4-8) or 'crossed' for fully crossed designs.
            corollary_dict (dict): A dictionary mapping corollary names to actual facet names.
                For example, {'p': 'persons', 'i': 'items'}.

            ```
        Returns:
            dict: A dictionary where keys are variance component names (strings), and
                  values are tuples of the corresponding facets.

        Example:
            >>> create_variance_tuple_dictionary(2, {'p': 'persons', 'i': 'items'})
            {
                'p': ('p',),
                'i:p': ('i', 'p'),
                'mean': ()
            }
        """
    variance_tuple_dictionary = {}

    try:
        if design_num == 'crossed':
            # each facet should be a separate variance component and crossed
            # get all possible combinations of facets
            for j in range(1, len(corollary_dict) + 1):
                for combo in combinations(corollary_dict.values(), j):
                    variance_tuple_dictionary[' x '.join(combo)] = combo

        elif design_num == 2:  # i:p
            variance_tuple_dictionary[corollary_dict['p']] = (corollary_dict['p'],)
            variance_tuple_dictionary[f'{corollary_dict["i"]}:{corollary_dict["p"]}'] = (corollary_dict['i'], corollary_dict['p'])

        elif design_num == 8:  # i:h:p
            variance_tuple_dictionary[corollary_dict['p']] = (corollary_dict['p'],)
            variance_tuple_dictionary[f'{corollary_dict["h"]}:{corollary_dict["p"]}'] = (corollary_dict['h'], corollary_dict['p'])
            variance_tuple_dictionary[f'{corollary_dict["i"]}:{corollary_dict["h"]}:{corollary_dict["p"]}'] = (corollary_dict['i'], corollary_dict['h'], corollary_dict['p'])

        elif design_num == 6:  # i:(p x h)
            variance_tuple_dictionary[corollary_dict['p']] = (corollary_dict['p'],)
            variance_tuple_dictionary[corollary_dict['h']] = (corollary_dict['h'],)
            variance_tuple_dictionary[f'{corollary_dict["p"]} x {corollary_dict["h"]}'] = (corollary_dict['p'], corollary_dict['h'])
            variance_tuple_dictionary[f'{corollary_dict["i"]}:({corollary_dict["p"]} x {corollary_dict["h"]})'] = (corollary_dict['i'], corollary_dict['p'], corollary_dict['h'])

        elif design_num == 5:  # (i:p) x h
            variance_tuple_dictionary[corollary_dict['p']] = (corollary_dict['p'],)
            variance_tuple_dictionary[corollary_dict['h']] = (corollary_dict['h'],)
            variance_tuple_dictionary[f'{corollary_dict["i"]}:{corollary_dict["p"]}'] = (corollary_dict['i'], corollary_dict['p'])
            variance_tuple_dictionary[f'{corollary_dict["p"]} x {corollary_dict["h"]}'] = (corollary_dict['p'], corollary_dict['h'])
            variance_tuple_dictionary[f'({corollary_dict["i"]}:{corollary_dict["p"]}) x {corollary_dict["h"]}'] = (corollary_dict['i'], corollary_dict['p'], corollary_dict['h'])

        elif design_num == 4:  # p x (i:h)
            variance_tuple_dictionary[corollary_dict['p']] = (corollary_dict['p'],)
            variance_tuple_dictionary[corollary_dict['h']] = (corollary_dict['h'],)
            variance_tuple_dictionary[f'{corollary_dict["i"]}:{corollary_dict["h"]}'] = (corollary_dict['i'], corollary_dict['h'])
            variance_tuple_dictionary[f'{corollary_dict["p"]} x {corollary_dict["h"]}'] = (corollary_dict['p'], corollary_dict['h'])
            variance_tuple_dictionary[f'{corollary_dict["p"]} x ({corollary_dict["i"]}:{corollary_dict["h"]})'] = (corollary_dict['p'], corollary_dict['i'], corollary_dict['h'])

        elif design_num == 7:  # (i x h):p
            variance_tuple_dictionary[corollary_dict['p']] = (corollary_dict['p'],)
            variance_tuple_dictionary[f'{corollary_dict["i"]}:{corollary_dict["p"]}'] = (corollary_dict['i'], corollary_dict['p'])
            variance_tuple_dictionary[f'{corollary_dict["h"]}:{corollary_dict["p"]}'] = (corollary_dict['h'], corollary_dict['p'])
            variance_tuple_dictionary[f'({corollary_dict["i"]} x {corollary_dict["h"]}):{corollary_dict["p"]}'] = (corollary_dict['i'], corollary_dict['h'], corollary_dict['p'])

        # Add the mean variance component
        variance_tuple_dictionary['mean'] = ()

    except Exception as e:
        raise ValueError(f"Error creating variance tuple dictionary: {str(e)}")

    return variance_tuple_dictionary


def parse_facets(design_num: Union[int, str], design_facets: list) -> Dict[str, tuple]:
    """
    Parses the facets of a research design and returns a dictionary of variance components.

    This function combines the functionality of `create_corollary_dictionary` and
    `create_variance_tuple_dictionary` to generate a comprehensive dictionary of
    variance components for a given research design.

    Parameters:
        design_num (Union[int, str]): The design number or 'crossed' for fully crossed designs.
        design_facets (list): List of facets extracted from the design string.

    Returns:
        Dict[str, tuple]: A dictionary where keys are variance component names (strings), and
                          values are tuples of the corresponding facets.

    Raises:
        ValueError: If the design pattern is invalid or can't be parsed.

    Example:
        >>> parse_facets(2, ['items', 'persons'])
        {
            'p': ('persons',),
            'i:p': ('items', 'persons'),
            'mean': ()
        }
    """
    corollary_dict = create_corollary_dictionary(design_num=design_num, design_facets=design_facets)
    variance_tuple_dict = create_variance_tuple_dictionary(design_num=design_num, corollary_dict=corollary_dict)

    return variance_tuple_dict

def get_facets_from_variance_tuple_dictionary(
        variance_tuple_dict: Dict[str, tuple]
) -> List[str]:
    """
    Extracts the facets from a variance tuple dictionary.

    Parameters:
        variance_tuple_dict (Dict[str, tuple]): A dictionary where keys are variance component names (strings),
                                                 and values are tuples of the corresponding facets.

    Returns:
        List[str]: A list of unique facets extracted from the variance tuple dictionary.
    """
    facets = set()
    for key, value in variance_tuple_dict.items():
        if key != 'mean':
            facets.update(value)
    
    return list(facets)

