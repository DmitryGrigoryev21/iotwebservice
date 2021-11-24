class utildb():
    @staticmethod
    def insert(table: str, data: object) -> str:
        columns = ",".join(vars(data).keys())
        values = ""
        for v in vars(data).values():
            if len(values) > 0:
                values += ","
            if type(v) == int:
                values += str(v)
            else:
                values += "\"%s\"" % v
        sql = "insert into %s (%s) values (%s)" % (table, columns, values)

        return sql

    @staticmethod
    def select_all(table: str) -> str:
        return "select * from %s" % table

    @staticmethod
    def select_by_id(table: str, id: int) -> str:
        return "select * from %s where id=%d" % (table, id)

    @staticmethod
    def select_all_where(table: str, recordcolumn: str, recordval: any) -> str:
        if type(recordval) == int:
            sql = "select * from %s where %s = %s" % (table, recordcolumn, recordval)
        else:
            sql = "select * from %s where %s = \"%s\"" % (table, recordcolumn, recordval)
        print(sql)
        return sql

    @staticmethod
    def update_by_id(table: str, data: object, id: int) -> str:
        columns = []
        values = []
        sql = "update %s set " % (table)
        for k, v in vars(data).items():
            sql += "%s=\"%s\"," % (k, v)
        sql = sql[:-1]
        sql += " where id=%d" % (id)
        return sql

    @staticmethod
    def delete_by_id(table: str, id: int) -> str:
        return "delete from %s where id=%d" % (table, id)

    @staticmethod
    def delete_all(table: str) -> str:
        return "delete from %s" % (table)