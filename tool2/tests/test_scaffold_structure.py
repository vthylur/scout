import os

def test_scaffold_directories_exist():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for d in ["src", "tests", "docker", "docs"]:
        assert os.path.isdir(os.path.join(base, d)), f"missing directory: {d}"
