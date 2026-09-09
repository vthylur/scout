from pathlib import Path


def test_tool1a_interface_confirmation_doc_exists_and_is_non_empty():
    doc_path = Path("tool2/docs/tool1a_interface_confirmed.md")

    assert doc_path.exists()
    assert doc_path.read_text(encoding="utf-8").strip()
