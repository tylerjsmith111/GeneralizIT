# GeneralizIT: Generalizability Theory Analysis in Python

## Overview

GeneralizIT is a Python-based library designed for conducting Generalizability Theory (GT) analyses. The library supports multiple research designs and provides tools to calculate ANOVA tables, generalizability coefficients (G coefficients), and decision (D) studies.

Generalizability Theory extends classical test theory by estimating multiple sources of error variance, providing a more flexible and detailed approach to reliability assessment. This makes it particularly useful for researchers and practitioners who work with multi-faceted designs and want to quantify the reliability and generalizability of their measurements across different facets (e.g., raters, items, occasions).

## Features

- **Support for Various Designs:** Handles different research designs (fully crossed, partially nested) with user-friendly syntax
- **Robust to Data Issues:** Supports unbalanced designs and can handle missing data
- **Automated Data Cleaning:** Prepares your data by dropping unnecessary columns and normalizing names.
- **ANOVA Calculation:** Produces ANOVA tables specific to your design using Analogous ANOVA based on Henderson's Method I
- **G Coefficients:** Computes generalizability coefficients to assess reliability.
- **D Studies:** Performs decision studies with customizable levels for facets to optimize measurement protocols
- **Summaries:** Provides concise summaries for ANOVA, G coefficients, and D studies

## Installation
```python
pip install generalizit
```
It is recommended to create a Python environment with Python 3.8 or higher.

The following dependencies are installed alongside the package:

- `pandas`
- `numpy`
- `scipy`

## Usage

### Initializing GeneralizIT

```python
from generalizit import GeneralizIT

# Initialize with:
# - `data`: A pandas DataFrame containing your data.
# - `input_str`: A string describing the research design (e.g., "Person x i x o").
# - `response`: The column name for the response variable.
GT = GeneralizIT(data=formatted_df, input_str='Person x i x o', response='Response')
```

### Example Workflow

```python
# Import the package
from generalizit import GeneralizIT
import pandas as pd

# Load data
data = pd.read_csv("your_data.csv")

# Initialize with your research design
GT = GeneralizIT(data=data, input_str='Person x i x o', response='Response')

# 1. Calculate ANOVA
GT.calculate_anova()
GT.anova_summary()

# 2. Compute G Coefficients
GT.calculate_g_coefficients()
GT.g_coefficients_summary()

# 3. Perform a D Study with different facet levels
GT.calculate_d_study(levels={'Person': [8], 'i': [4, 8], 'o': [1, 2]})
GT.d_study_summary()

# 4. Calculate Confidence Intervals
GT.calculate_confidence_intervals(alpha=0.05)
GT.confidence_intervals_summary()
```

### Input Data Format
The data should be structureda as a pandas DataFrame in a long format, where each row corresponds to a unique combination of the facets and the response variable.

 ```markdown
  | Person | i | o | Response |
  |--------|---|---|----------|
  |      1 | 1 | 1 |        2 |
  |      1 | 2 | 1 |        6 |
  |      1 | 3 | 1 |        7 |
  |      1 | 4 | 1 |        5 |
  |      1 | 1 | 2 |        2 |
  |      1 | 2 | 2 |        5 |
  |      1 | 3 | 2 |        5 |
  |      1 | 4 | 2 |        5 |
  ...
  |     10 | 1 | 1 |        6 |
  |     10 | 2 | 1 |        8 |
  |     10 | 3 | 1 |        7 |
  |     10 | 4 | 1 |        6 |
  |     10 | 1 | 2 |        6 |
  |     10 | 2 | 2 |        8 |
  |     10 | 3 | 2 |        8 |
  |     10 | 4 | 2 |        6 |
  ```
Conversely, if the design was nested such as `person x (rater:item)`, raters are nested under item and should be identified uniquely either by delineation `item1_rater1` or unique numbering as below:

``` markdown
| Person | item | rater | Response |
|--------|------|-------|----------|
|      1 |    1 |     1 |        2 |
|      1 |    1 |     2 |        6 |
|      1 |    1 |     3 |        7 |
|      1 |    1 |     4 |        5 |
|      1 |    2 |     5 |        2 |
|      1 |    2 |     6 |        5 |
|      1 |    2 |     7 |        5 |
|      1 |    2 |     8 |        5 |
|      1 |    3 |     9 |        6 |
|      1 |    3 |    10 |        8 |
|      1 |    3 |    11 |        7 |
|      1 |    3 |    12 |        6 |
|      2 |    1 |     1 |        6 |
|      2 |    1 |     2 |        8 |
|      2 |    1 |     3 |        8 |
|      2 |    1 |     4 |        6 |
...
```

### Example Datasets

#### Synthetic Data from Brennan (2001)

The package includes examples of synthetic data used to demonstrate the functionality of the library.
These are located in the 'tests' directory. 
You can adapt these examples to your own datasets.

## Research Design Syntax

The `input_str` parameter specifies the research design. Supported formats include:

- **Crossed Designs:** `"Person x i x o"`
- **Nested Designs:** `"Person x (r:t)"`

## Output

- **ANOVA Table:** Provides variance component estimates for each facet.
- **G Coefficients:**
  - Phi (Φ): Absolute coefficient for dependability
  - Rho² (ρ²): Relative coefficient for generalizability
- **D Studies:** Offers predictions of generalizability for specified facet levels to optimize measurement protocols
- **Confidence Intervals:** Calculates confidence intervals for means of each facet.
- **Summaries:** Concise summaries of ANOVA, G coefficients, D studies, and Confidence Intervals.

## Advanced Tutorials

Advanced package usage and G-Theory methodology tutorials and are available in the [tutorials directory](https://github.com/tylerjsmith111/GeneralizIT/tree/main/tutorials) of our GitHub repository.

## Notes

- Include only the necessary facets and the response variable.
- Column names should match those specified in the research design.\
- For unbalanced designs, GeneralizIT will automatically use appropriate computational methods

## Citation
If you use GeneralizIT in your research, please cite the following paper:
```bibtex
@software{GeneralizIT,
  author = {Smith, T.J. and Kline, T.J.B. and Kline, A.},
  title = {GeneralizIT: A Python Solution for Generalizability Theory Computations},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/tylerjsmith111/GeneralizIT},
  version = {0.1.0}
}
```

## License

This library is licensed under the MIT License.

## Contributions

Contributions to improve functionality or expand supported designs are welcome! Please fork the repository and create a pull request.

## Contact

For questions or support, raise an issue in the github repo!

---

Happy analyzing with **GeneralizIT**!
