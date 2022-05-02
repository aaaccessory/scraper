from db.db import MySQLConnector


class Article(MySQLConnector):

    def find_article(self, data_array):
        table_name = "teams"
        keys = ["id"]

        return self.__find(table_name, keys, data_array)

    def insert_articles(self, data):
        cursor = self.mysql_connection.cursor()

        cursor.execute("START TRANSACTION")

        insertion_statement = (
            "insert into article (productTitle, content, price, reviewNumber, photo, url, keywordId) "
            "values (%s, %s, %s, %s, %s, %s, %s)"
        )
        try:
            cursor.execute(insertion_statement, (data["title"], data["product_future"], data["price"], data["review_number"], data["product_image"], data['product_url'], data['keywordId']))
        except Exception as e:
            cursor.execute("ROLLBACK")
            print(data)
            raise e
        cursor.execute("COMMIT")

    def insert(self):
        print("insert")

    def article_exists(self, url):
        cursor = self.mysql_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM article where url = '" + url +"'")
        result = cursor.fetchall()
        if len(result) > 0:
            return True
        return False

    def update(self):
        print("update")

    def delete(self):
        print("delete")
