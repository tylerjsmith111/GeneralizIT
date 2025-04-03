import pytest
from generalizit.design_utils import match_research_design, parse_facets

@pytest.mark.utils
@pytest.mark.parametrize("input_str, expected_num", [
    ("persons x raters", "crossed"),
    ("items:persons", 2),
    ("raters x items x helpers", "crossed"),
    ("raters x (persons:items)", 4),
    ("(items:persons) x helpers", 5),
    ("items:(persons x helpers)", 6),
    ("(doctors x items): raters", 7),
    ("xylophones:helpers:persons", 8)
])
def test_match_research_design(input_str, expected_num):
    """Test function to verify design pattern matching"""
    num_result, _ = match_research_design(input_str)
    assert num_result == expected_num, f"Failed for {input_str}. Got {num_result}, expected {expected_num}"

@pytest.mark.utils
@pytest.mark.parametrize("input_str, expected_tuples", [
    ("persons x raters", {
        "persons": ("persons",),
        "raters": ("raters",),
        "persons x raters": ("persons", "raters"),
        "mean": ()
    }),
    ("items:persons", {
        "persons": ("persons",),
        "items:persons": ("items", "persons"),
        "mean": ()
    }),
    ("raters x (items:helpers)", {
        "raters": ("raters",),
        "helpers": ("helpers",),
        "items:helpers": ("items", "helpers"),
        "raters x helpers": ("raters", "helpers"),
        "raters x (items:helpers)": ("raters", "items", "helpers"),
        "mean": ()
    })
])
def test_parse_facets(input_str, expected_tuples):
    """Test function to verify variance tuple dictionary creation"""
    num_result, facets = match_research_design(input_str)
    result = parse_facets(design_num=num_result, design_facets=facets)
    
    # Check that all expected keys are present
    for key in expected_tuples:
        assert key in result, f"Missing key '{key}' in result"
    
    # Check that all expected tuples match
    for key, value in expected_tuples.items():
        assert result[key] == value, f"For key '{key}', expected {value}, got {result[key]}"