import pytest
import pandas as pd
from generalizit.design import Design
from generalizit.design_utils import match_research_design, parse_facets, validate_research_design
from tests.design_test_base import DesignTestBase

@pytest.fixture
def test_design2():
    # synthetic dataset for item:person
    # Brennan (2001) Synthetic Data # 2

    # First we parse the input string to get the research design
    design_str = "item:person"
    design_num, facets = match_research_design(design_str)
    
    # Validate the research design
    try:
        validate_research_design(design_num)
    except ValueError as e:
        raise ValueError(e)

    variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)
    

    # Create the data object
    data = {
        'person': list(range(1, 11)),
        'personi_item1': [2, 4, 5, 5, 4, 4, 2, 3, 0, 6],
        'personi_item2': [6, 5, 5, 9, 3, 4, 6, 4, 5, 8],
        'personi_item3': [7, 6, 4, 8, 5, 4, 6, 4, 4, 7],
        'personi_item4': [5, 7, 6, 6, 6, 7, 5, 5, 5, 6],
        'personi_item5': [2, 6, 5, 5, 4, 6, 2, 6, 5, 6],
        'personi_item6': [5, 7, 4, 7, 5, 4, 7, 6, 5, 8],
        'personi_item7': [5, 5, 5, 7, 6, 7, 7, 6, 5, 8],
        'personi_item8': [5, 7, 5, 6, 4, 8, 5, 4, 3, 6]
    }

    # Convert wide data to long format for Design2
    formatted_data = {
        'person': [],
        'item': [],
        'Response': []
    }

    for person in range(1, 11):
        for item in range(1, 9):
            key = f'personi_item{item}'
            formatted_data['person'].append(person)
            formatted_data['item'].append(item)
            formatted_data['Response'].append(data[key][person - 1])

    synthetic_data = pd.DataFrame(formatted_data)

    t_values_dict = {
        'person': 2288.2500,
        'item:person': 2430.0000,
        'mean': 2226.0500
    }

    variances_dict = {
        'person': 0.6108,
        'item:person': 2.0250
    }

    rho_dict = {
        'person': 0.71,
    }

    phi_dict = {
        'person': 0.71,
    }
    
    # ---- Unused ----
    levels_dict = {
        'person': 10,
        'item': 8
    }

    deg_freedom_dict = {
        'person': 9,
        'item:person': 70
    }
    
    ss_values_dict = {
        'person': 62.20,
        'item:person': 141.75
    }

    ms_values_dict = {
        'person': 6.9111,
        'item:person': 2.0250
    }

    return DesignTestBase(
        design=Design(data=synthetic_data, variance_tuple_dictionary=variance_tuple_dictionary, response_col='Response'),
        levels_df=None,
        t_values_dict=t_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict
    )