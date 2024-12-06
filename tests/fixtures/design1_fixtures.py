import pytest
import pandas as pd
from tests.testdesign import TestDesign
from generalizit.designcrossed import DesignCrossed

@pytest.fixture
def test_design1():
    # synthetic dataset for person x item
    # Brennan (2001) Synthetic Data # 1

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

    levels_dict = {
        'person': 10,
        'item': 12
    }

    deg_freedom_dict = {
        'person': 9,
        'item': 11,
        'person x item': 99
    }

    t_values_dict = {
        'person': 44.75,
        'item': 47.10,
        'person x item': 67.00
    }

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

