# Contributing to GeneralizIT

Thank you for considering contributing to GeneralizIT! Your help is essential in improving the project for everyone. Below are the guidelines and processes we follow for contributions.

## Table of Contents

1.  [Code of Conduct](#code-of-conduct)
2.  [How to Contribute](#how-to-contribute)
   *   [Reporting Issues](#reporting-issues)
   *   [Suggesting Enhancements](#suggesting-enhancements)
   *   [Submitting Pull Requests](#submitting-pull-requests)
3.  [Development Setup](#development-setup)
4.  [Style Guide](#style-guide)
5.  [Maintainers and Review Process](#maintainers-and-review-process)

## 1. Code of Conduct

This project adheres to a strict Code of Conduct. All contributors are expected to foster a welcoming and inclusive environment. Please review our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## 2. How to Contribute

We welcome contributions in many forms:

*   Bug fixes
*   New features
*   Documentation improvements
*   Code refactoring and cleanup

### Reporting Issues

If you find a bug or wish to request a feature, please open an issue at:

[https://github.com/tylerjsmith111/GeneralizIT/issues](https://github.com/tylerjsmith111/GeneralizIT/issues)

Include:

*   A clear title and description
*   Steps to reproduce the issue
*   Expected vs. actual behavior
*   Any relevant logs or screenshots

Issue labels we use include:

*   `bug`
*   `enhancement`
*   `documentation`
*   `help wanted`

### Suggesting Enhancements

For ideas to improve GeneralizIT, please open an issue. Describe:

*   The current behavior/limitation
*   Your proposed enhancement and its benefits
*   Any potential impacts on the current codebase

### Submitting Pull Requests

Before submitting a pull request (PR), please:

1.  Fork the repository
2.  Clone your fork:

   ```bash
   git clone https://github.com/<your-username>/GeneralizIT.git
   ```
3.  Create a new branch for your contribution:

   ```bash
   git checkout -b feature/your-feature-name
   ```
4.  Make changes – ensure you follow the coding style guidelines.
5.  Test your changes. If you are adding new features or fixing bugs, please add tests to ensure your changes work as expected.
   You can run the tests using:

   ```bash
   pytest
   ```

   If you are modifying existing code, ensure that all tests pass.
   If you are adding new tests, please ensure they are included in the test suite.
6.  Commit your changes with a clear and descriptive message, e.g.:

   ```bash
   git commit -m "Fix: Corrected variance calculation in design.py"
   ```
7.  Push your changes to your branch:

   ```bash
   git push origin feature/your-feature-name
   ```
8.  Open a PR on GitHub against the `main` branch of [https://github.com/tylerjsmith111/GeneralizIT](https://github.com/tylerjsmith111/GeneralizIT)

Make sure your PR is linked to the appropriate issue. Include tests if applicable and a detailed description of your changes.

## 3. Development Setup

To set up GeneralizIT on your local machine:

1.  Clone the repository:

   ```bash
   git clone https://github.com/tylerjsmith111/GeneralizIT.git
   ```
2.  Navigate into the project directory:

   ```bash
   cd GeneralizIT/development
   ```
3.  Install dependencies:

   ```bash
   pip install -e .[test]
   ```

   (This will install the package in editable mode along with the required dependencies for testing.)
4.  Run tests to ensure everything is set up correctly:

   ```bash
   pytest
   ```

## 4. Style Guide

*   Follow [PEP 8](https://peps.python.org/pep-0008/) guidelines for Python.
*   Write meaningful commit messages.
*   Document your functions and classes appropriately.
*   Update tests if your changes affect the existing functionality.
*   Avoid unnecessary whitespace and maintain clean code.

## 5. Maintainers and Review Process

Our maintainers are responsible for reviewing and merging contributions. When you submit a PR:

*   It will be reviewed by one of our maintainers.
*   You may receive feedback or requested changes.
*   Once approved, your PR will be merged.

If you have any questions or need assistance, please raise a discussion in our [GitHub Discussions](https://github.com/tylerjsmith111/GeneralizIT/discussions) or contact one of the maintainers directly.

Thank you for contributing to GeneralizIT!
Happy coding and happy analyzing!

