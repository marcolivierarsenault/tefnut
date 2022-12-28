def load_fixture(filename):
    """Load a fixture."""
    with open(filename, encoding="utf-8") as fptr:
        return fptr.read()
