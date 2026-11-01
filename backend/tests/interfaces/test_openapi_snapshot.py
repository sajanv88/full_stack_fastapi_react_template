import json
import os
from pathlib import Path

from api import app

SNAPSHOT = Path(__file__).parents[2] / "openapi.json"


def test_api_matches_the_committed_contract():
    """
    frontend/app/src/api is generated from this contract, so a difference here is a change
    for its consumers. If it is intended, update the contract with UPDATE_OPENAPI=1 pytest
    and regenerate the client.
    """
    current = json.loads(json.dumps(app.openapi()))

    if os.environ.get("UPDATE_OPENAPI"):
        SNAPSHOT.write_bytes((json.dumps(current, indent=2, sort_keys=True) + "\n").encode("utf-8"))

    assert json.loads(SNAPSHOT.read_text(encoding="utf-8")) == current
