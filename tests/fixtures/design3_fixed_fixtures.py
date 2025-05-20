# --------
# This file uses synthetic dataset #3 with I fixed from
# @book{brennan_generalizability_2001,
# 	address = {New York, NY},
# 	author = {Brennan, Robert L.},
# 	publisher = {Springer New York},
# 	title = {Generalizability {Theory}},
# 	year = {2001}}
# --------
import pytest
import pandas as pd
from tests.design_test_base import DesignTestBase
from generalizit.design import Design
from generalizit.design_utils import match_research_design, parse_facets, validate_research_design


@pytest.fixture
def test_design3_fixed():
    # synthetic dataset for person x i x o
    # Brennan (2001) Synthetic Data # 3
    
    design_str = "person x i x o"
    design_num, facets = match_research_design(design_str)
    
    # Validate the research design
    try:
        validate_research_design(design_num)
    except ValueError as e:
        raise ValueError(e)

    variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)

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

    # New DataFrame with 'Person', 'i', 'o', and 'Response'
    new_data = {
        'person': [],
        'i': [],
        'o': [],
        'Response': []
    }

    # Populate the new DataFrame
    for person in range(1, 11):
        for o in [1, 2]:  # Assuming 'O1' and 'O2'
            for i in range(1, 5):  # Assuming 'i1', 'i2', 'i3', 'i4'
                key = f'O{o}_i{i}'
                response = df.at[person - 1, key]
                new_data['person'].append(person)
                new_data['i'].append(i)
                new_data['o'].append(o)
                new_data['Response'].append(response)

    # Convert to DataFrame
    synthetic_data = pd.DataFrame(new_data)
    
    t_values_dict = {
        'person': 2288.25,
        'i': 2263.50,
        'o': 2229.25,
        'person x i': 2382.00,
        'person x o': 2303.50,
        'i x o': 2274.20,
        'person x i x o': 2430.00
    }

    variances_dict = {
        'person': 0.5528,
        'i': .4417,
        'o': 0.0074,
        'person x i': 0.5750,
        'person x o': 0.1009,
        'i x o': 0.1565,
        'person x i x o': 0.9352
    }

    rho_dict = {
        'person': 0.81
    }

    phi_dict = {
        'person': 0.79
    }
    
    return DesignTestBase(
        design=Design(data=synthetic_data, variance_tuple_dictionary=variance_tuple_dictionary, response_col='Response'),
        levels_df=None,
        t_values_dict=t_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict
    )