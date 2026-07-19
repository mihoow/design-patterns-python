# Project overview

This repository demonstrates design patterns from
"Design Patterns: Elements of Reusable Object-Oriented Software"
using Python.

Each design pattern should have its own directory containing:

- `<pattern_name>.py`
- `test_<pattern_name>.py`
- `diagram.puml`

The main Python file should contain a small executable console example.

# Python style

- Use 4 spaces for indentation.
- Do not use tabs.
- Keep lines at or below 79 characters.
- Use docstrings for public modules, classes, methods, and functions.
- Use UpperCamelCase for class names.
- Use lowercase_snake_case for functions, methods, and variables.
- Use `self` as the first argument of instance methods.

# Tests

- Use pytest.
- Run all tests with:

  `python -m pytest`

- Each pattern should have unit tests covering its essential behavior.
- Do not test implementation details unless necessary.

# Quality checks

Before completing a change, run:

- `python -m ruff check .`
- `python -m ruff format --check .`
- `python -m pytest`

# Design pattern examples

- Keep examples focused on the demonstrated pattern.
- Clearly separate pattern participants from demonstration code.
- Include `if __name__ == "__main__":` for executable examples.
- When Python has a more idiomatic alternative, mention it separately.

# Additional

- Everything has to be in English.
- You do not write PlantUML diagrams yourself
- You ask for clarification always, for the smallest unknown
