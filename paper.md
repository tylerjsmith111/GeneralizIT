---
title: "GeneralizIT: A Python Solution for Generalizability Theory Computations"
tags:
  - Python
  - statistics
  - generalizability
authors:
  - name: Tyler J. Smith
    orcid: 0009-0003-6761-0540
    affiliation: "1, 2, 3" # (Multiple affiliations must be quoted)
  - name: Theresa Kline
    affiliation: 4
  - name: Adrienne Kline
    orcid: 0000-0002-0052-0685
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: "1, 2, 3"
affiliations:
  - name: Center for Artificial Intelligence, Northwestern Medicine, Chicago, IL, USA
    index: 1
  - name: Division of Cardiac Surgery, Northwestern University, Chicago, IL, USA
    index: 2
  - name: Dept. of Electrical and Computer Engineering, Northwestern University, Chicago, IL, USA
    index: 3
  - name: University of Calgary, Calgary, Canada
    index: 4
date: 27 November 2024
bibliography: paper.bib
---

<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/x-mathjax-config">
  MathJax.Hub.Config({ tex2jax: {inlineMath: [['$', '$']]}, messageStyle: "none" });
</script>


# Summary

`GeneralizIT` is a Python package designed to streamline the application of Generalizability Theory (G-Theory) in research and practice.
G-Theory extends classical test theory by estimating multiple sources of error variance, providing a more flexible and detailed approach to reliability assessment.
Despite its advantages, G-Theory's complexity can present a significant barrier to researchers.
`GeneralizIT` addresses this challenge by offering an intuitive, user-friendly mechanism to calculate variance components, generalizability coefficients ($E\rho^2$) and dependability ($\Phi$) and to perform decision (D) studies. 
D-Studies allow users to make decisions about potential study designs and target improvements in the reliability of certain facets.
The package supports both fully crossed and nested designs, enabling users to perform in-depth reliability analysis with minimal coding effort.
With built-in visualization tools and detailed reporting functions, `GeneralizIT` empowers researchers across disciplines, such as education, psychology, healthcare, and the social sciences, to harness the power of G-Theory for robust evidence-based insights.
 Whether applied to small or large datasets, `GeneralizIT` offers an accessible and computationally efficient solution to improve measurement reliability in complex data environments.

# Statement of need

Generalizability Theory (G-Theory) offers a powerful extension to Classical Test Theory by enabling the estimation of multiple sources of error variance, providing a more nuanced and comprehensive approach to assessing measurement reliability [@brennan:2010].
However, its inherent complexity often limits its accessibility, particularly for researchers who lack advanced statistical training or coding expertise [@teker:2015]. This presents a significant barrier to its widespread adoption. 

Currently, no Python-based package exists for conducting Generalizability Theory (G-Theory) analyses. The current implementations require proprietary or specialized statistical software such as SAS, SPSS, EduG, G-String-MV [@bloch:2012], [@bloch:2024], or the R package `gtheory` [@moore:2016]. **Table 1** provides an updated summary of the available software for G-Theory analyses [@briesch:2014]. These tools require steep learning curves that may not be accessible to the growing number of Python-based researchers, leaving many relying on less robust methods for reliability analysis.

Table 1: Summary of available software for G-Theory analyses

| **Software**        | **Availability**                                                                                     | **Input**                    | **Missing Data** | **Unbalanced Designs (a)** | **D Studies** |
|----------------------|-----------------------------------------------------------------------------------------------------|------------------------------|------------------|----------------------------|---------------|
| G-String MV (b)  | Free download from [GitHub](https://github.com/G-String-Legacy/GS_MV/releases)                      | Raw data                   | N (c)            | Y                          | Y             |
| SAS VARCOMP     | Included in SAS Package                                                                             | Raw data                   | Y (d)            | Y                          | N             |
| SPSS VARCOMP    | Included in SPSS Advanced Statistics option                                                         | Raw data                   | Y (e)            | Y                          | N             |
| EduG            | Free download from [IRD](http://www.irdp.ch/edumetrie/englishprogram.htm)                           | Raw data or sums of squares | N                | N                          | Y             |
| gtheory         | R package                                                                                          | Raw data                   | N                | Y                          | Y             |
| **GeneralizIT**      | Python package                                                                                     | Raw data                   | N                | N                          | Y             |



**Notes:**

- (a) Unbalanced designs refer to unequal numbers of observations per group. 

- (b) G_String_MV is legacy software designed for multivariate G-theory analysis.

- (c) Missing data handling is not supported.

- (d) Limited missing data handling available in SAS.

- (e) SPSS provides extensive missing data handling options.


The `GeneralizIT` Python package addresses this critical need by offering a user-friendly platform that simplifies the application of G-Theory in research and practice. By automating the calculation of variance components, generalizability coefficients, and dependability indices, GeneralizIT makes this sophisticated theory accessible to a broad range of disciplines, including education, psychology, healthcare, and the social sciences. The package supports crossed experimental designs for any number of facets enabling users to conduct detailed reliability analyses without extensive coding knowledge. Additionally, its built-in visualization and reporting tools provide clear, interpretable outputs, further enhancing its utility.

In a research landscape where measurement reliability is paramount for producing valid, evidence-based conclusions, GeneralizIT fills an urgent need for a computationally efficient and accessible solution. It democratizes the use of G-Theory, allowing researchers to obtain more reliable insights even from complex, small, or large datasets.

# Methods
The package relies on equations from [@brennan:2001] and [@cardinet:1976] to calculate variance components, generalizability and dependability coefficients, confidence intervals, and D-Studies. The following sections provide an overview of the key equations and methods used in GeneralizIT.

## Fully Crossed Designs

### Calculating Sum of Squares for Variance Components
First Calculate T Values:
$$
T(\alpha) = \pi(\alpha^*) \sum \left( \bar{\alpha} \right)^2
$$

where $\pi(\alpha^*)$ is the product of levels of all facets except $\alpha$. 

Then:
$$
SS(\alpha) = T(\alpha) + (-1)^1 \left( \sum T(\beta) \text{ for } \beta \in \alpha \right) + (-1)^2 \left( \sum T(\gamma) \text{ for } \gamma \in \alpha \right) - \ldots + (-1)^n T(U)
$$


where $n$ is the number of facets in $\alpha$.  
$\beta$ is a subset of interactions of length $n - 1$ facets in $\alpha$.  
$\gamma$ is a subset of interactions of length $n - 2$ facets in $\alpha$.  
...


Finally Mean Squares:
$$
MS(\alpha) = \frac{SS(\alpha)}{Df(\alpha)}
$$

For example:
$$
SS(AB) = T(AB) - (T(A) + T(B)) + T(U)
$$

$$
MS(AB) = \frac{SS(AB)}{Df(AB)}
$$

### Calculating Variance Components
$\sigma^2(\alpha) = \frac{1}{\pi(\alpha^*)}$ [linear combination of mean squares (MS)]

where $\pi(\alpha^*)$ is the product of levels of all facets except $\alpha$.

The linear combination of mean squares is determined by the following algorithm:

Identify all components that consist of the $t$ indices in $\alpha$ and exactly one additional index; and call the set of "additional" indices $A$.

- Step 0: $MS(\alpha)$

- Step 1: $-$ mean squares for all components that consist of $t$ indices in $\alpha$ and exactly one of the indices in $A$

- Step 2: $+$ mean squares for all components that consist of $t$ indices in $\alpha$ and any two of the indices in $A$
$$
\vdots
$$
- Step $n$: $+ (-1)^n$ [mean squares for all components that consist of $t$ indices in $\alpha$ and $n$ of the indices in $A$]


For example:
$$
\sigma^2(a) = \frac{MS(a) - MS(ab) - MS(ac) + MS(abc)}{b \cdot c}
$$  

## Nested Designs
`GeneralizIT` allows for designs with nesting for designs with 1 object of measurement and 1 or 2 facets of differentiation. For these designs, the user provided string is compared to tables in appendix A and B of @brennan:2001 to properly calculate variance components.

## Generalizability Coefficient $E\rho^2$ and Dependability Coefficient $\Phi$
$$
E\rho^2 = \frac{\sigma^2(\tau)}{\sigma^2(\tau) + \sigma^2(\delta)}
$$

$$
\sigma^2(\tau) = \sigma^2(\alpha) + \frac{\sigma^2(\alpha_{\text{fixed}})}{n_{\text{fixed}}}
$$

Where $\alpha_{\text{fixed}}$ represents all interaction variances between $\alpha$ and ONLY fixed factors.

$$
\sigma^2(\delta) = \frac{\sigma^2(\alpha_{\text{random}})}{n_{\text{random}}}
$$

Where $\alpha_{\text{random}}$ represents all interaction variances between $\alpha$ and ONLY random factors.

$$
\Phi = \frac{\sigma^2(\tau)}{\sigma^2(\tau) + \sigma^2(\Delta)} 
$$

Where $\Delta$ is the sum of all variances except the variance of $\tau$.


## D-Study Method

To conduct a D-Study, $\sigma^2(\alpha)$ calculated from the G-Study are held constant for each facet and interaction, $\alpha$, while the levels for each facet are varied according to user input. The formulas from the [Generalizability Coefficient $E\rho^2$ and Dependability Coefficient $\Phi$](#generalizability-coefficient-e\rho^2-and-dependability-coefficient-Φ) are then repeated for each potential combination to return G-Coefficients for each potential G-Study design. 

## Confidence Intervals 
Variation of expected scores for each object of measurement can be calculated as follows:

$$
\sigma^2(aBC) = \frac{\sigma^2(b)}{n_b} + \frac{\sigma^2(c)}{n_c} + \frac{\sigma^2(bc)}{n_b n_c} + \frac{\sigma^2(ab)}{n_b} + \frac{\sigma^2(ac)}{n_c} + \frac{\sigma^2(abc)}{n_b n_c}
$$

$$
\bar{X}\_{aBC} = \bar{X}\_{aBC} \pm z\_{\frac{\alpha}{2}} \cdot \sqrt{\sigma^2(aBC)}
$$

Where $n$ is the levels for each facet, $\bar{X}\_{aBC}$ is the expected score of object of measurement $a$ with respect to facets $b$ and $c$, and $z\_{\frac{\alpha}{2}}$ is the z-score for the desired confidence level.


# Code Usage and Availability
`GeneralizIT` is available on PyPI and can be installed using pip:

```bash
pip install generalizit
```

The package is open-source and available on GitHub at [https://github.com/tylerjsmith111/GeneralizIT](GeneralizIT). In addition to the code, the repository includes detailed documentation and synthetic datasets from @brennan:2001 to facilitate user testing and validation.

# Conclusion

`GeneralizIT` is a Python package that simplifies the application of Generalizability Theory in research and practice. By automating the calculation of variance components, generalizability and dependability coefficients, and conducting D-Studies, `GeneralizIT` empowers researchers to conduct robust reliability analyses with minimal coding effort in an analysis environment with which they are familiar. Currently, no Python package exists for conducting G-Theory analyses, creating a significant barrier to its widespread adoption. This work addresses this critical need by providing a user-friendly platform for balanced crossed and nested designs. While other G-Theory software solutions allow for analyses that take into account missing data and/or work with unbalanced designs, they are more user intensive and/or proprietary. We reserve these features for future work. Presently, `GeneralizIT` offers an accessible, computationally efficient solution for improving measurement reliability in diverse research environments. By democratizing the use of G-Theory, `GeneralizIT` provides a valuable resource for researchers seeking to enhance the validity and reliability of their measurement instruments and make sound statistically informed decisions.

# Acknowledgements

We do not have any financial support to disclose. 

# References
