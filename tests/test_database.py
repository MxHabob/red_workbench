from redteam.core.workspace import create_engagement, get_db

def test_engagement_initializes_database(tmp_path, monkeypatch):
    monkeypatch.setenv("RTW_HOME", str(tmp_path))
    create_engagement("unit-test")
    db = get_db("unit-test")
    assert db.rows("assets") == []
    assert db.rows("findings") == []
