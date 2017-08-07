import pytest
from database import Database


def add_column(db):
    db.addColumn("test_table", "test_column_2")


def populate_db(db):
    db.insert("test_table", "name", "John", "test_column", 25)
    db.insert("test_table", test_column=50, name="Johnny")
    db.insert("test_table", **{'test_column': 75, "name": "George"})


@pytest.fixture(scope="function")
def database():
    return Database()


@pytest.fixture(scope="function")
def database_with_tab(database):
    db = database
    tab_name = "test_table"
    db.createTableAutoID(tab_name, "name CHAR(16) UNIQUE NOT NULL", "test_column INTEGER")
    return db


@pytest.fixture(scope="function")
def populated_database(database_with_tab):
    db = database_with_tab
    populate_db(db)
    return db


def test_db_createTable_ut(database):
    tab_name = "test_table"
    db = database
    db.createTableAutoID(tab_name)
    assert db.isTableExist(tab_name)
    tab_name2 = "test_table2"
    db.createTable(tab_name2, "ID INTEGER UNIQUE", "name CHAR(16) UNIQUE NOT NULL", "test_column INTEGER")
    assert db.isTableExist(tab_name2)


def test_db_isTableExist_ut(database_with_tab):
    db = database_with_tab
    assert db.isTableExist("test_table")
    assert not db.isTableExist("other")


def test_db_addColumn_ut(database_with_tab):
    db = database_with_tab
    add_column(db)


def test_db_insert_ut(database_with_tab):
    db = database_with_tab
    populate_db(db)


def test_db_insertUpdate_ut(database_with_tab):
    db = database_with_tab
    db.insertReplace("test_table", test_column=25, name="test")
    data = db.get("test_table", "*")
    assert (1, "test", 25,) == data[0]
    db.insertReplace("test_table", test_column=50, name="test", update="test_column")
    data = db.get("test_table", "test_column")
    assert (50,) == data[0]


def test_db_update_ut(populated_database):
    db = populated_database
    db.update("test_table", "test_column", 101, condition="ID = 2")
    assert (2, 'Johnny', 101) in db.getTable("test_table")
    db.update("test_table", test_column=102, condition="ID = 2")
    assert (2, 'Johnny', 102) in db.getTable("test_table")
    db.update("test_table", **{'test_column': 103, 'condition': "ID = 2"})
    assert (2, 'Johnny', 103) in db.getTable("test_table")


def test_db_getTable_ut(populated_database):
    db = populated_database
    tab = db.getTable("test_table")
    assert tab


def test_db_get_ut(populated_database):
    db = populated_database
    data = db.get("test_table", "*")
    assert (1, u"John", 25) in data
    assert (2, u"Johnny", 50) in data
    assert (3, u"George", 75) in data
    data = db.get("test_table", "*", condition="name = 'Johnny'")
    assert (2, u"Johnny", 50) in data
    data = db.get("test_table", "test_column", condition="name = 'Johnny'")
    assert (50,) in data
    data = db.get("test_table", test_column=None, condition="name = 'John'")
    assert (25,) in data
