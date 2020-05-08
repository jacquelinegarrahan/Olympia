from olympia import db
from sqlalchemy.engine.result import ResultProxy


def test_database_select():
    selection = db.execute_query("SELECT * FROM midis WHERE midi_id=:id", {"id": 2})
    assert isinstance(selection, (ResultProxy,))
