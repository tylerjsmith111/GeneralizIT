import pandas as pd
from generalizit.design_utils import parse_facets, match_research_design, validate_research_design
from generalizit.generalizit import GeneralizIT

if __name__ == "__main__":
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
                    response = df.at[person - 1, key]
                    new_data['person'].append(person)
                    new_data['t'].append(t)
                    new_data['r'].append(r)
                    new_data['Response'].append(response)

    # Convert to DataFrame
    syn4_df = pd.DataFrame(new_data)

    design_str = 'person x (r:t)'

    # # match the research design
    # design_num, facets = match_research_design(design_str)
    #
    # # validate the research design
    # try:
    #     validate_research_design(design_num)
    # except ValueError as e:
    #     raise ValueError(f"Invalid research design: {e}")
    #
    # # parse the facets
    # variance_tup_dict = parse_facets(design_num=design_num, design_facets=facets)

    GT = GeneralizIT(data=syn4_df, design_str=design_str, response='Response')

    GT.calculate_anova()

    GT.calculate_g_coefficients()

    GT.anova_summary()
    GT.g_coefficients_summary()
    GT.variance_summary()

    # ---------------------------------------------------------
    # SYNTHETIC DATA FROM BRENNAN (2001) - SYTNHETIC DATA SET NO. 3

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

    print(df.head(10))

    # New DataFrame with 'Person', 'i', 'o', and 'Response'
    new_data = {
        'Person': [],
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
                new_data['Person'].append(person)
                new_data['i'].append(i)
                new_data['o'].append(o)
                new_data['Response'].append(response)

    # Convert to DataFrame
    formatted_df = pd.DataFrame(new_data)

    print(formatted_df.head(8))
    print(formatted_df.tail(8))

    GT = GeneralizIT(data=formatted_df, design_str='Person x i x o', response='Response')

    GT.calculate_anova()
    GT.calculate_g_coefficients()

    GT.anova_summary()
    GT.g_coefficients_summary()

    # GT.calculate_d_study(levels={'Person': None, 'i': [4, 8], 'o': [1, 2]})
    # GT.d_study_summary()
    #
    # GT.calculate_confidence_intervals(alpha=0.05)
    # GT.confidence_intervals_summary()

    # # ---------------------------------------------------------