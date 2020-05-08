import sqlalchemy as db
from sqlalchemy import select
from sqlalchemy.sql import text
from olympia import CONFIGS


class DB:
    def __init__(self):
        self.engine = db.create_engine(
            f"mysql+pymysql://{CONFIGS['MySQL']['db_user']}:{CONFIGS['MySQL']['db_password']}@{CONFIGS['MySQL']['db_endpoint']}/{'olympia'}"
        )
        self.connection = self.engine.connect()


def insert(table_name, value_dict):
    database = DB()
    metadata = db.MetaData()
    table = db.Table(table_name, metadata, autoload=True, autoload_with=database.engine)
    query = table.insert().values(**value_dict)
    database.connection.execute(query)


def execute_query(query, params):
    database = DB()
    statement = text(query)
    results = database.connection.execute(statement, params)
    return results


if __name__ == "__main__":
    execute_query("SELECT * FROM midis WHERE midi_id=:id", {"id": 2})
