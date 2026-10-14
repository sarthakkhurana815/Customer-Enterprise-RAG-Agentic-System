from pathlib import Path


def test_generator_script_exists():
    root = Path(__file__).resolve().parents[1]
    assert (root / "scripts" / "generate_dataset.py").exists()
