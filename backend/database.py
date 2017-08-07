import sqlite3


class Database(object):
    def __init__(self, db=":memory:"):
        super(Database, self).__init__()
        self.con = sqlite3.connect(db)

    def __del__(self):
        self.con.close()

    def createTable(self, tab_name, column_with_type, *args, **kwargs):
        columns = [column_with_type]
        columns += [c for c in args]
        columns = ", ".join(columns) if columns else ''
        cmd = _DatabaseCMDs.CREATE.format(tab_name, columns)
        self.__exec_cmd(cmd, None)

    def createTableAutoID(self, tab_name, *args, **kwargs):
        columns = [c for c in args]
        columns = ", " + ", ".join(columns) if columns else ''
        cmd = _DatabaseCMDs.CREATE_AUTO_ID_TAB.format(tab_name, columns)
        self.__exec_cmd(cmd, None)

    def isTableExist(self, tab_name):
        cmd = (_DatabaseCMDs.SELECT + "WHERE type=\'table\' and name=\'{}\'").format('count(*)', 'sqlite_master', tab_name)
        cursor = self.con.cursor()
        cursor.execute(cmd)
        try:
            return cursor.fetchall().pop()[0] == 1
        except IndexError:
            return False

    def addColumn(self, tab_name, column_name, column_type='CHAR(64)'):
        cmd = (_DatabaseCMDs.ALTER + _DatabaseCMDs.ADD_COLUMN).format(tab_name, column_name, column_type)
        self.__exec_cmd(cmd, None)

    def insert(self, tab_name, *args, **kwargs):
        columns = []
        values = []
        pargs = self.__prepareArgs(args, kwargs)
        for c, v in pargs:
            columns.append(c)
            values.append(str(v))
        cmd = _DatabaseCMDs.INSERT.format(tab_name, ", ".join(columns), ", ".join(["?" for _v in values]))
        self.__exec_cmd(cmd, values)

    def __exec_cmd(self, cmd, values):
        tvalues = tuple(values) if values else tuple()
        self.con.cursor().execute(cmd, tvalues)
        self.__commit()

    def insertReplace(self, tab_name, *args, **kwargs):
        columns = []
        values = []
        pargs = self.__prepareArgs(args, kwargs)
        for c, v in pargs:
            columns.append(c)
            values.append(v)
        cmd = _DatabaseCMDs.INSERT_REPLACE.format(tab_name, ", ".join(columns), ", ".join(["?" for _v in values]))
        self.__exec_cmd(cmd, values)

    def update(self, tab_name, *args, **kwargs):
        pargs = self.__prepareArgs(args, kwargs)
        columns = ["{} = {}".format(c, v) for c, v in pargs]
        cmd = _DatabaseCMDs.UPDATE_TAB.format(tab_name, ", ".join(columns))
        cmd += self.__addCondition(kwargs)
        self.__exec_cmd(cmd, None)

    def __prepareArgs(self, args, kwargs):
        other = ['condition', 'update']
        args = (args[0], None) if len(args) == 1 else args
        pargs = [(args[i], args[i + 1]) for i in range(0, int(len(args) + 1 / 2), 2)]
        pargs += [(k, v) for k, v in kwargs.items() if k not in other]
        return pargs

    def getTable(self, tab_name):
        cmd = _DatabaseCMDs.SELECT.format("*", tab_name)
        cursor = self.con.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def get(self, tab_name, *args, **kwargs):
        pargs = self.__prepareArgs(args, kwargs)
        columns = [c for c, v in pargs]
        cmd = _DatabaseCMDs.SELECT.format(", ".join(columns), tab_name)
        cmd += self.__addCondition(kwargs)
        cursor = self.con.cursor()
        cursor.execute(cmd)
        return cursor.fetchall()

    def __addCondition(self, kwargs):
        condition = kwargs.get('condition', None)
        if condition:
            return _DatabaseCMDs.CONDITION.format(condition)
        return str()

    def __commit(self):
        self.con.commit()


class _DatabaseCMDs:
    CREATE = "CREATE TABLE {} ({}) "  # tab name
    CREATE_AUTO_ID_TAB = "CREATE TABLE {} (ID INTEGER PRIMARY KEY AUTOINCREMENT {}) "  # tab name
    ALTER = "ALTER TABLE {} "  # tab name
    RENAME = "RENAME TO {} "  # tab name
    SELECT = "SELECT {} FROM {} "  # columns; tab name
    UPDATE = "UPDATE {} "
    UPDATE_TAB = UPDATE + "SET {} "  # tab_name; columnX = valueX
    CONDITION = "WHERE {} "  # condition i.e.: ID = 6
    DROP = "DROP TABLE {} "  # tab name;
    ADD_COLUMN = "ADD COLUMN {} {} "  # column; type
    INSERT = "INSERT INTO {} ({}) VALUES ({}) "  # tab name; columns; ? * values
    INSERT_REPLACE = "INSERT OR REPLACE INTO {} ({}) VALUES ({}) "
    INSERT_FROM_TAB = "INSERT INTO {} ({}) SELECT {} FROM {} "  # tab name; columns; ? * values
