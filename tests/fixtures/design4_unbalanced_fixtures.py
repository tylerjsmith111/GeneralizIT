import pytest
import pandas as pd
from tests.design_test_base import DesignTestBase
from generalizit.design import Design
from generalizit.design_utils import match_research_design, parse_facets, validate_research_design


@pytest.fixture
def test_design4_unbalanced():
    # Unbalanced synthetic dataset for person (p), item (i), category (h) p x (i:h)
    # Brennan (2001) Synthetic Data # 4
    
    # First we parse the input string to get the research design
    design_str = "p x (i:h)"
    design_num, facets = match_research_design(design_str)
    
    # Validate the research design
    try:
        validate_research_design(design_num)
    except ValueError as e:
        raise ValueError(e)

    variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)

    # Brennan Synthetic Unbalanced Data #4
    data = {
        'p': range(1, 9),
        'h1_i1': [4, 2, 2, 1, 3, 1, 3, 0],
        'h1_i2': [5, 1, 4, 3, 3, 2, 5, 1],
        'h2_i1': [3, 2, 4, 5, 6, 5, 6, 1],
        'h2_i2': [3, 3, 7, 4, 7, 6, 8 ,2],
        'h2_i3': [5, 1, 6, 5, 5, 4, 6, 0],
        'h2_i4': [4, 4, 5, 5, 7, 4, 7, 4],
        'h3_i1': [5, 4, 8, 4, 8, 5 ,7, 7],
        'h3_i2': [7, 6, 7, 5, 9, 6, 8, 8],
    }

    df = pd.DataFrame(data)

    # New DataFrame with columns 'person', 'h', 'i', 'Response'
    new_data = {
        'p': [],
        'h': [],
        'i': [],
        'Response': []
    }

    # Populate the new DataFrame
    for person in range(1, 9):
        for h in [1, 2, 3]:  # Assuming 't1', 't2', 't3'
            for i in range(1, 5):  # Assuming 'i1' to 'i4'
                key = f'h{h}_i{i}'
                # check if the key exists
                if key in df.columns:
                    response = df.at[person-1, key]
                    new_data['p'].append(person)
                    new_data['h'].append(h)
                    new_data['i'].append(i)
                    new_data['Response'].append(response)

    # Convert to DataFrame
    synthetic_data = pd.DataFrame(new_data)
    
    # Create the T values dictionary
    t_values_dict = {
        'p': 1390.0,
        'h': 1424.0,
        'i:h': 1440.0,
        'p x h': 1564.5,
        'p x (i:h)': 1610.0,
        'mean': 1296.0
    }

    # Create the variances dictionary
    variances_dict = {
            'p': 1.2014,
            'h': 2.9161,
            'i:h': 0.2946,
            'p x h': 0.9913,
            'p x (i:h)': .8429,
        }

    # Create the rho dictionary
    rho_dict = {
        'p': 0.716,
    }

    # Create the phi dictionary
    phi_dict = {
        'p': 0.4277,
    }
    
    
    return DesignTestBase(
        design=Design(data=synthetic_data, variance_tuple_dictionary=variance_tuple_dictionary, response_col='Response'),
        levels_df=None,
        t_values_dict=t_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict
    )