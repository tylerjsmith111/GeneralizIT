# --------
# This file uses synthetic dataset Huynh (1977) from
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
def test_design1():
    # synthetic dataset for person x item
    # Brennan (2001) Synthetic Data # 1
    
    # First we parse the input string to get the research design
    design_str = "person x item"
    design_num, facets = match_research_design(design_str)
    
    # Validate the research design
    try:
        validate_research_design(design_num)
    except ValueError as e:
        raise ValueError(e)

    variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)

    data = [
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]

    formatted_data = {
        'person': [],
        'item': [],
        'Response': []
    }

    for person in range(1, 11):
        for item in range(1, 13):
            formatted_data['person'].append(person)
            formatted_data['item'].append(item)
            formatted_data['Response'].append(data[person-1][item-1])

    synthetic_data = pd.DataFrame(formatted_data)

    t_values_dict = {
        'person': 44.75,
        'item': 47.10,
        'person x item': 67.00
    }

    variances_dict = {
        'person': 0.0574,
        'item': 0.0754,
        'person x item': 0.1269
    }

    rho_dict = {
        'person': 0.844
    }

    phi_dict = {
        'person': 0.773
    }
    
    d_study_expected = {
        'person: 10, item: 5': pd.DataFrame({
            'rho^2': [.693],
            'phi^2': [0.586]
        }, index=['person']),
        'person: 10, item: 10': pd.DataFrame({
            'rho^2': [.819],
            'phi^2': [0.740]
        }, index=['person']),
        'person: 10, item: 15': pd.DataFrame({
            'rho^2': [.871],
            'phi^2': [0.810]
        }, index=['person']),
        'person: 10, item: 20': pd.DataFrame({
            'rho^2': [.901],
            'phi^2': [0.850]
        }, index=['person']),
    }
    
    # ---- Unused ----
    ss_values_dict = {
        'person': 7.3417,
        'item': 9.6917,
        'person x item': 12.5583
    }

    ms_values_dict = {
        'person': 0.8157,
        'item': 0.8811,
        'person x item': .1269
    }
    
    levels_dict = {
        'person': 10,
        'item': 12
    }

    deg_freedom_dict = {
        'person': 9,
        'item': 11,
        'person x item': 99
    }

    return DesignTestBase(
        design=Design(data=synthetic_data, variance_tuple_dictionary=variance_tuple_dictionary, response_col='Response'),
        levels_df=None,
        t_values_dict=t_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict,
        d_study_expected=d_study_expected
    )

