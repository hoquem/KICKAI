---

#### `.cursor/rules/06_documentation.md`
How we document our code for future clarity.

```markdown
# Documentation Standards

All Python code, including modules, classes, and functions, must have Google-style docstrings. Document the purpose, arguments, return values, and any exceptions raised.

Example:
\`\`\`python
def my_function(param1: int) -> str:
    """Does a thing.

    Args:
        param1: The first parameter.

    Returns:
        A string representation.
    """
    # ...
\`\`\`