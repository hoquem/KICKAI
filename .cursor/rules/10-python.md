# Python rules (concise, production-ready)

- Write clear, readable code with meaningful names; avoid single-letter identifiers.
- Add type hints for public APIs; skip redundant annotations for trivially inferred locals.
- Handle edge cases first with guard clauses; avoid deep nesting and large try/except blocks.
- Never catch broad exceptions without meaningful handling.
- Only comment when explaining non-obvious decisions; keep comments short.
- Match existing formatting and indentation; do not reformat unrelated code.
- Keep dependencies minimal; import only what’s used.
