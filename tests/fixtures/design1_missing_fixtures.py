import pytest
import pandas as pd
from tests.design_test_base import DesignTestBase
from generalizit.design import Design
from generalizit.design_utils import match_research_design, parse_facets, validate_research_design


@pytest.fixture
def test_design1_missing():
    # synthetic dataset for person x item
    # Brennan (2001) Synthetic Data # 1
    
    # First we parse the input string to get the research design
    design_str = "p x i"
    design_num, facets = match_research_design(design_str)
    
    # Validate the research design
    try:
        validate_research_design(design_num)
    except ValueError as e:
        raise ValueError(e)

    variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)

    data_raw = [
        [1, 1, 1, 1, 1, 0, 1],
        [2, 1, 0, 1, 1, 1, 1],
        [3, None, 1, 1, 1, 0, 0],
        [4, 0, None, None, 1, 0, 1],
        [5, 1, None, 0, 1, 0, None],
        [6, 1, 1, 1, 1, 0, 1],
        [7, 0, None, 1, None, 0, 0],
        [8, 0, None, 1, 1, 1, 1],
        [9, 1, 1, 0, 1, None, 0],
        [10, None, 0, 0, 0, None, 0],
        [11, 1, 1, 1, 1, 1, 1],
        [12, None, 0, None, 0, 0, 1]
    ]

    # Create DataFrame with appropriate column names
    data = pd.DataFrame(data_raw, columns=['p', 'i_1', 'i_2', 'i_3', 'i_4', 'i_5', 'i_6'])

    formatted_data = {
        'p': [],
        'i': [],
        'Response': []
    }

    for person in range(1, 13):
        for item in range(1, 7):
            response = data.loc[data['p'] == person, f'i_{item}'].values[0]
            # Only add non-null values
            if pd.notna(response):
                formatted_data['p'].append(person)
                formatted_data['i'].append(item)
                formatted_data['Response'].append(response)

    synthetic_data = pd.DataFrame(formatted_data)

    t_values_dict = {
        'p': 27.8,
        'i': 24.7432,
        'p x i': 37.0,
        'mean': 23.2034
    }


    variances_dict = {
        'p': 0.0473,
        'i': 0.0117,
        'p x i': 0.1840
    }

    rho_dict = {
        'p': 0.5507
    }

    phi_dict = {
        'p': 0.5354
    }



    return DesignTestBase(
        design=Design(data=synthetic_data, variance_tuple_dictionary=variance_tuple_dictionary, response_col='Response', missing_data=True),
        levels_df=None,
        t_values_dict=t_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict
    )
