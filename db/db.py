import json
import mysql.connector


class MySQLConnector:
    def __init__(self, config):
        self.mysql_connection = mysql.connector.connection.MySQLConnection(
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=(config["port"] if "port" in config else 3306),
            database=config["database"],
        )

    def __find(self, table_name, keys, data):
        cursor = self.mysql_connection.cursor(dictionary=True)

        db_keys = []
        values = []

        for key in keys:
            if data[key] is not None:
                db_keys.append("`{}`=%s".format(key))
                values.append(data[key])
            else:
                db_keys.append("`{}` is NULL".format(key))

        selection_statement = ("SELECT * FROM {} WHERE {};").format(
            table_name, " AND ".join(db_keys)
        )

        try:
            cursor.execute(selection_statement, tuple(values))
            result = cursor.fetchall()
            cursor.execute("COMMIT;")
            cursor.close()
            return result
        except Exception as e:
            print("Table: {}".format(table_name))
            print("Keys: {}".format(keys))
            print("Values: {}".format(values))
            print("Selection Statement: {}".format(selection_statement))
            raise e

    def __delete(self, table_name, keys, data):
        cursor = self.mysql_connection.cursor()

        cursor.execute("START TRANSACTION")

        values = []

        for key in keys:
            values.append(data[key])

        keys_string = ["`{}`=%s".format(key) for key in keys]
        keys_string = " AND ".join(keys_string)

        deletion_statement = ("DELETE FROM {} " "WHERE {}").format(
            table_name, keys_string
        )

        try:
            cursor.execute(deletion_statement, values)
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Table: {}".format(table_name))
            print("Keys: {}".format(keys))
            print("Values: {}".format(values))
            print("Deletion Statement: {}".format(deletion_statement))
            raise e

    def __insert(self, table_name, keys, data, updates=[]):
        cursor = self.mysql_connection.cursor()

        cursor.execute("START TRANSACTION")

        values = []

        for key in keys:
            values.append(data[key])

        keys = ["`{}`".format(key) for key in keys]

        insertion_statement = ("INSERT INTO {} " "({}) " "VALUES ({})").format(
            table_name, ",".join(keys), ",".join(["%s"] * len(keys))
        )

        if len(updates) > 0:
            insertion_statement = "{} ON DUPLICATE KEY UPDATE {}".format(
                insertion_statement, ",".join(["`{}`=%s".format(x) for x in updates])
            )

        for key in updates:
            values.append(data[key])

        try:
            cursor.execute(insertion_statement, tuple(values))
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Table: {}".format(table_name))
            print("Keys: {}".format(keys))
            print("Values: {}".format(values))
            print("Updates: {}".format(updates))
            print("Insertion Statement: {}".format(insertion_statement))
            raise e

        last_row_id = cursor.lastrowid

        # Take care of the `cursor.lastrowid` above.
        # COMMIT must be executed after last_row_id is extracted.
        cursor.execute("COMMIT;")

        return last_row_id

    def __update(
        self,
        table_name,
        update_keys,
        update_data,
        where_keys,
        where_data,
        delete_conflicting=True,
    ):
        cursor = self.mysql_connection.cursor()

        cursor.execute("START TRANSACTION")

        update_values = []

        for key in update_keys:
            update_values.append(update_data[key])

        modified_update_keys = ["`{}`=%s".format(key) for key in update_keys]

        where_values = []

        for key in where_keys:
            where_values.append(where_data[key])

        modified_where_keys = ["`{}`=%s".format(key) for key in where_keys]

        update_statement = ("UPDATE IGNORE {} " "SET {} " "WHERE {}").format(
            table_name, ",".join(modified_update_keys), ",".join(modified_where_keys)
        )

        values = update_values + where_values

        try:
            cursor.execute(update_statement, tuple(values))
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Table: {}".format(table_name))
            print("Update Keys: {}".format(update_keys))
            print("Where Keys: {}".format(where_keys))
            print("Values: {}".format(values))
            print("Update Statement: {}".format(update_statement))
            raise e

        if delete_conflicting:
            # Delete conflicting rows
            self.__delete(table_name, where_keys, where_data)