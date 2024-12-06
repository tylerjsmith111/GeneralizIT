import pytest
import pandas as pd
from generalizit.designcrossed import DesignCrossed
from tests.testdesign import TestDesign

@pytest.fixture
def test_design3():
    # synthetic dataset for person x o x i
    # Brennan (2001) Synthetic Data # 3

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

    levels_dict = {
        'person': 10,
        'i': 4,
        'o': 2
    }

    deg_freedom_dict = {
        'person': 9,
        'i': 3,
        'o': 1,
        'person x i': 27,
        'person x o': 9,
        'i x o': 3,
        'person x i x o': 27,
        'Total': 79
    }

    t_values_dict = {
        'person': 2288.25,
        'i': 2263.50,
        'o': 2229.25,
        'person x i': 2382.00,
        'person x o': 2303.50,
        'i x o': 2274.20,
        'person x i x o': 2430.00
    }

    ss_values_dict = {
        'person': 62.20,
        'i': 37.45,
        'o': 3.20,
        'person x i': 56.30,
        'person x o': 12.05,
        'i x o': 7.50,
        'person x i x o': 25.25
    }

    ms_values_dict = {
        'person': 6.9111,
        'i': 12.4833,
        'o': 3.2000,
        'person x i': 2.0852,
        'person x o': 1.3383,
        'i x o': 2.5000,
        'person x i x o': 0.9352
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
        'person': 0.64
    }

    phi_dict = {
        'person': 0.55
    }

    return TestDesign(
        design=DesignCrossed(synthetic_data),
        levels_dict=levels_dict,
        deg_freedom_dict=deg_freedom_dict,
        t_values_dict=t_values_dict,
        ss_values_dict=ss_values_dict,
        ms_values_dict=ms_values_dict,
        variances_dict=variances_dict,
        rho_dict=rho_dict,
        phi_dict=phi_dict
    )