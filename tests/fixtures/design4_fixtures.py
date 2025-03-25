import pytest
import pandas as pd
from generalizit.design_utils import match_research_design, parse_facets, validate_research_design
from generalizit.design import Design
from tests.design_test_base import DesignTestBase



@pytest.fixture
def test_design4():
    # synthetic dataset for person x (r:t)
    # Brennan (2001) Synthetic Data # 4

    design_str = "person x (r:t)"
    design_num, facets = match_research_design(design_str)
    
    # Validate the research design
    try:
        validate_research_design(design_num)
    except ValueError as e:
        raise ValueError(e)

    variance_tuple_dictionary = parse_facets(design_num=design_num, design_facets=facets)


    data = {
        'person': range(1, 11),
        't1_r1': [5, 9, 3, 7, 9, 3, 7, 5, 9, 4],
        't1_r2': [6, 3, 4, 5, 2, 4, 3, 8, 9, 4],
        't1_r3': [5, 7, 3, 5, 9, 3, 7, 5, 8, 4],
        't1_r4': [5, 7, 3, 3, 7, 5, 7, 7, 8, 3],
        't2_r5': [5, 7, 5, 3, 7, 3, 7, 7, 6, 3],
        't2_r6': [3, 5, 3, 1, 7, 3, 5, 5, 6, 5],
        't2_r7': [4, 5, 3, 4, 3, 6, 5, 5, 6, 6],
        't2_r8': [5, 5, 5, 3, 7, 3, 7, 4, 5, 5],
        't3_r9': [6, 7, 6, 5, 2, 4, 5, 3, 5, 5],
        't3_r10': [7, 7, 5, 3, 7, 5, 5, 2, 8, 7],
        't3_r11': [3, 5, 1, 3, 5, 1, 5, 1, 1, 1],
        't3_r12': [3, 2, 6, 5, 3, 2, 4, 1, 1, 1]
    }

    df = pd.DataFrame(data)

    # New DataFrame with columns 'person', 't', 'r', 'Response'
    new_data = {
        'person': [],
        't': [],
        'r': [],
        'Response': []
    }

    # Populate the new DataFrame
    for person in range(1, 11):
        for t in [1, 2, 3]:  # Assuming 't1', 't2', 't3'
            for r in range(1, 13):  # Assuming 'r1' to 'r12'
                key = f't{t}_r{r}'
                # check if the key exists
                if key in df.columns:
                    response = df.at[person-1, key]
                    new_data['person'].append(person)
                    new_data['t'].append(t)
                    new_data['r'].append(r)
                    new_data['Response'].append(response)

    # Convert to DataFrame
    synthetic_data = pd.DataFrame(new_data)

    # Create the T values dictionary
    t_values_dict = {
        'person': 2800.1667,
        't': 2755.7000,
        'r:t': 2835.4000,
        'person x t': 2931.5000,
        'person x (r:t)': 3204.0000,
        'mean': 2707.5
    }

    # Create the variances dictionary
    variances_dict = {
            'person': 0.4731,
            't': 0.3252,
            'r:t': 0.6475,
            'person x t': 0.5596,
            'person x (r:t)': 2.3802,
        }

    # Create the rho dictionary
    rho_dict = {
        'person': 0.55,
    }

    # Create the phi dictionary
    phi_dict = {
        'person': 0.46,
    }

    # ---- Unused ----
    # Create the levels dictionary
    levels_dict = {
        'person': 10,
        'r': 4,
        't': 3
    }

    # Create the degrees of freedom dictionary
    deg_freedom_dict = {
        'person': 9,
        't': 2,
        'r:t': 9,
        'person x t': 18,
        'person x (r:t)': 81
    }
    
    # Create the SS values dictionary
    ss_values_dict = {
        'person': 92.6667,
        't': 48.2000,
        'r:t': 79.7000,
        'person x t': 83.1333,
        'person x (r:t)': 192.8000,
    }

    # Create the MS values dictionary
    ms_values_dict = {
        'person': 10.2963,
        't': 24.1000,
        'r:t': 8.8556,
        'person x t': 4.6185,
        'person x (r:t)': 2.3802,
    }
    
    return DesignTestBase(
        design=Design(data=synthetic_data, variance_tuple_dictionary=variance_tuple_dictionary, response_col='Response'),
        levels_df=None,
        t_values_dict=t_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict
    )