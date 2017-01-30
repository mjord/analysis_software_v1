import sqlite3
import sys

class Database():
    host = "localhost"
    user = "testusr"
    passwd = "El0G742"

    # db = "student-schedule"

    def __init__(self, **kwargs):
        if "db_name" not in kwargs:
            print("Need to supply a location when defining a database!")
            raise
        else:
            self.db = kwargs.get("db_name")

        try:
            self.connection = sqlite3.connect(self.db)

        except sqlite3.Error as e:

            print("Error %s:" % e.args[0])
            sys.exit(1)

    def query(self, q):
        try:
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute(q)
            self.connection.commit()

        except sqlite3.Error as e:

            print("Error %s:" % e.args[0])
            sys.exit(1)


        return cursor.fetchall()

    def __del__(self):
        self.connection.close()



if __name__ == "__main__":
    db = Database(db_name = "/Users/matthewjordan/Documents/Georgia Tech/Student-Schedule/student-schedule.sqlite")

    q = "DELETE FROM STUDENTS"

    q = "DELETE FROM CLASSES"
    db.query(q)

    q = """INSERT INTO STUDENTS
    (first_name, last_name, gtid)
    VALUES
    ('Matt', 'Jordan', 1234),
    ('Vanessa', 'Nau', 6789),
    ('George', 'Burdell', 1000);
    """
    db.query(q)

    q = """INSERT INTO CLASSES
        (NAME, DEPT, NUMBER, STUDENT_ID)
        VALUES
        ('Best Class', 'ECE', 440, 1),
        ('Best Class', 'ECE', 440, 2),
        ('Worst Class', 'CE', 100, 2),
        ('Avg Class', 'ME', 330, 1),
        ('Avg Class', 'ME', 330, 3);
        """
    db.query(q)

    q = "SELECT * FROM STUDENTS"
    r = db.query(q)

    q = "SELECT ROWID FROM STUDENTS WHERE GTID = 1000"
    r = db.query(q)

    q = """SELECT FIRST_NAME, LAST_NAME, DEPT, NUMBER
    FROM STUDENTS AS a
        INNER JOIN CLASSES AS b
        ON a.rowid = b.student_id
        ORDER BY DEPT;"""

    rows = db.query(q)
    for row in rows:
        print("%s %s is in %s: %i"%(row["first_name"], row["last_name"], row["dept"], row["number"]))