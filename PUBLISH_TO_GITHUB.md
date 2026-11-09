# SAMBU repository

The canonical GitHub repository is <https://github.com/bboroski/SAMBU>.

Clone it with:

\`\`\`bash
git clone https://github.com/bboroski/SAMBU.git
cd SAMBU
\`\`\`

For local development, create a virtual environment and install the package in editable mode:

\`\`\`bash
python -m venv .venv
. .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
python -m pip install -e .
\`\`\`

Run the examples and test suite with:

\`\`\`bash
sambu examples/ideal_gas.sambu
python -m unittest discover -s tests -v
\`\`\`

Contributions should include tests for new language features and preserve dimensional-safety checks.
