import re
from typing import Optional, Dict, Tuple

def match_research_design(input_string: str) -> Optional[int]:
    """
    Matches a string input of a research design to one of 8 predefined designs.
    
    Parameters:
        input_string (str): The research design input as a string.
            Valid operators are 'x' for crossing and ':' for nesting.
            Some designs require parentheses to indicate grouping.
    
    Returns:
        int: The design number (1 to 8) that matches the input
        None: If no match is found
    
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
    
    # AFTER (fixed code):
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
        print(f"Fully Crossed Design")
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

def parse_facets(design_num: int, design_facets: list) -> Dict[str, str]:
    """
    Parse a research design string and return a dictionary mapping facet types
    (p, i, h) to their actual values based on the design pattern.
    
    Parameters:
        design_num (int): The design number
        design_facets (list): List of facets extracted from the design string
        
    Returns:
        Dict[str, str]: Dictionary mapping facet types to their values
        Keys are 'p' (persons), 'i' (items), 'h' (helpers/raters)
        
    Raises:
        ValueError: If the design pattern is invalid or can't be parsed
    """
    
    # Initialize facets dictionary
    facets_dict = {}
    
    try:
        if design_num == 'crossed':
            return {f"facet_{i+1}": facet for i, facet in enumerate(design_facets)}
        
        elif design_num == 2:  # i:p
            facets_dict['i'] = design_facets[0]
            facets_dict['p'] = design_facets[1]
            
        elif design_num == 8:  # i:h:p
            facets_dict['i'] = design_facets[0]
            facets_dict['h'] = design_facets[1]
            facets_dict['p'] = design_facets[2]
        
        elif design_num == 6:  # i:(p x h)
            facets_dict['i'] = design_facets[0]
            facets_dict['p'] = design_facets[1]
            facets_dict['h'] = design_facets[2]
            
        elif design_num == 5:  # (i:p) x h
            facets_dict['i'] = design_facets[0]
            facets_dict['p'] = design_facets[1]
            facets_dict['h'] = design_facets[2]
                
        elif design_num == 4:  # p x (i:h)
            facets_dict['p'] = design_facets[0]
            facets_dict['i'] = design_facets[1]
            facets_dict['h'] = design_facets[2]
            
        elif design_num == 7:  # (i x h):p
            facets_dict['i'] = design_facets[0]
            facets_dict['h'] = design_facets[1]
            facets_dict['p'] = design_facets[2]
            
        # Verify all required facets are present
        required_facets = ['i', 'p']
        if design_num >= 3:  # Designs 3-8 require all three facets
            required_facets.append('h')
            
        missing_facets = [f for f in required_facets if f not in facets_dict]
        if missing_facets:
            raise ValueError(f"Missing required facets: {missing_facets}")
            
    except Exception as e:
        raise ValueError(f"Error parsing facets: {str(e)}")
        
    return facets_dict
            
            
# def print_design(design_num: int, facets_dict: Dict[str, str]):
#     """Prints the design number and facets in a readable format"""
#     design_names = {
#         2: "i:p",
#         4: "p x (i:h)",
#         5: "(i:p) x h",
#         6: "i:(p x h)",
#         7: "(i x h):p",
#         8: "i:h:p"
#     }
    
#     # Print the design number, facets, and design
#     print(f"Design {design_num}: {design_names[design_num]}")
#     print("Facets:")
#     for _, facet in facets_dict.items():
#         print(f" {facet}")
    
#     # Reprint the design replacing 'i', 'p', 'h' with actual facet values
#     start = 0
#     design_str = design_names[design_num]
#     for key, value in facets_dict.items():
#         design_str = design_str[:start] + design_str[start:].replace(key, value)
#         # Find the end of the replaced value
#         start = design_str.index(value) + len(value)
#     print(f"Design: {design_str}")
    


# Run tests
# if __name__ == "__main__":
#     test_parse_facets()
    # Test cases including problematic facets
    # test_cases = [
    #     "xylaphones:helpers:persons",  # Should work now
    #     "x y:helpers:persons",         # Should raise error (empty facets)
    #     "facets x helpers:persons",     # Should work
    #     "matrix x helpers:persons",    # Should work
    #     "xbox:helpers:persons"         # Should work
    # ]

    # for test in test_cases:
    #     try:
    #         result = match_research_design(test)
    #         print(f"✓ Success: {test} -> Design {result}")
    #     except ValueError as e:
    #         print(f"✗ Error: {test} -> {str(e)}")
    
    
    # p x (r:t) design 7