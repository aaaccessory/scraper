from db.db import MySQLConnector


class Keyword(MySQLConnector):

    def find_keyword(self, data_array):
        table_name = "teams"
        keys = ["id"]

        return self.__find(table_name, keys, data_array)

    def insert_keywords(self, data_array):
        cursor = self.mysql_connection.cursor()

        cursor.execute("START TRANSACTION")

        insertion_statement = (
            "insert into keyword (keyword, scrapeDate"
            "values (%s, %s)"
        )
        try:
            for data in data_array:
                cursor.execute(insertion_statement, (data["keyword"], data["scrapeDate"]))
        except Exception as e:
            cursor.execute("ROLLBACK")
            print(data_array)
            raise e
        cursor.execute("COMMIT")

    def insert(self):
        print("insert")

    def select(self):
        cursor = self.mysql_connection.cursor(dictionary=True)
        # cursor.execute("SELECT * FROM keyword")
        cursor.execute("SELECT * FROM keyword where scraped = 0")
        # cursor.execute("SELECT * FROM keyword where scraped = 0 and DATE(`scrapeDate`) = CURDATE()")
        result = cursor.fetchall()
        return result

    def keyword_scraped(self, keywordId):
        cursor = self.mysql_connection.cursor()
        cursor.execute("START TRANSACTION")
        update_statement = "UPDATE keyword SET scraped = true, synced = false WHERE id= " + str(keywordId)

        try:
            cursor.execute(update_statement)
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Update Statement: {}".format(update_statement))
            raise e


    def update(self):
        print("update")

    def update_scrape_date(self, date, keyword_id):
        time = date.strftime('%Y-%m-%d %H:%M:%S')
        cursor = self.mysql_connection.cursor()
        cursor.execute("START TRANSACTION")
        update_statement = "UPDATE keyword SET updatedAt = '"+time +"', scraped = false WHERE id= " + str(keyword_id)

        try:
            cursor.execute(update_statement)
            cursor.execute("COMMIT;")
        except Exception as e:
            cursor.execute("ROLLBACK")
            print("Update Statement: {}".format(update_statement))
            raise e

    def delete(self):
        print("delete")