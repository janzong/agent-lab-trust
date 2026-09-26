import json

from agent_lab_trust.cli import main


def test_deletion_proof_is_clean_and_hashed(capsys) -> None:
    exit_code = main(["deletion-proof"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["before_count"] == 3
    assert payload["after_count"] == 0
    assert payload["idempotent_delete_count"] == 0
    assert payload["clean"] is True
    assert len(payload["audit_hash"]) == 16
