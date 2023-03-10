import sqlite3
from _decimal import Decimal
from datetime import date
from data_handler import *
from BillAPI import BillAPI
from data_handler import Bill, BillCreate, User, UserCreate
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

todays_date = date.today()
class BillDBAPI(BillAPI):
    def create_user(self, UserCreate):
        #connects to db we name,if it doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # generate UUID
        id = uuid4().hex
        
        # hash password
        hashed_pass =  generate_password_hash(UserCreate.password)
        c.execute("INSERT INTO Users VALUES (?,?,?,?)", (id, 
        UserCreate.username,
        hashed_pass,
        UserCreate.email))

        conn.commit()
        conn.close()
    def get_all_users(self) -> list[User]:

        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # Query the whole DB
        c.execute("SELECT * FROM Users")
        fetched = c.fetchall()

        # Commit our command
        conn.commit()

        # Close our connection
        conn.close()
        deserialized_users= deserialize_rows(User, fetched)
        return deserialized_users
    def get_user_by_username(self, username: str) -> User:
        """Gets user from database searching by username and returns full user obj"""

        # connects to db we name,if table doesnt exist will create it

        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username = ? ", [username])
        user_row = c.fetchall()

        conn.commit()
        conn.close()
        user = deserialize_row(User, user_row)
        return user
    def get_user_by_id(self, id: str) -> User:
        """Gets user from database searching by id and returns full user obj"""

        # connects to db we name,if table doesnt exist will create it

        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE user_id = ? ", [id])
        user_row = c.fetchall()

        conn.commit()
        conn.close()
        user = deserialize_row(User, user_row)
        return user
    def delete_all_users(self):
        pass
    def create_bill(self, new_bill: BillCreate, user_id:str) -> Bill:
        """Takes BillCreate (Bill without ID), and adds to database 
        and returns the Bill object with the ID
        """
        # connects to db we name,if it doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # generate UUID
        id = uuid4().hex
        
        c.execute("INSERT INTO bills VALUES (?,?,?,?,?)", (id, new_bill.name,
                                                            dollars_to_cents(new_bill.amount),
                                                            new_bill.due_date, user_id))

        conn.commit()
        conn.close()

        # return bill not that its been created in DB so it can be returned to user

        # returns created bill
        return deserialize_row(Bill, self.get_bill_by_id(id),todays_date)

    # Query the DB return all records
    def get_all_bills(self, user_id:str) -> list[Bill]:
        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        # Query the whole DB
        c.execute("SELECT * FROM bills WHERE user_id=?", [user_id])
        fetched = c.fetchall()

        # Commit our command
        conn.commit()

        # Close our connection
        conn.close()
        deserialized_bills = deserialize_rows(Bill, fetched)
        return deserialized_bills

    def get_bill_by_id(self, id: str) -> list[tuple[object]]:
        # connects to db we name,if table doesn't exist will create it
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("SELECT * FROM bills WHERE id = ? ", [id])
        bill_row = c.fetchall()

        conn.commit()
        conn.close()

        return bill_row

    def delete_bill_by_id(self, id: str) -> dict:
        """ Deletes bill from database"""
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("DELETE FROM bills WHERE id = ? ", [id])

        conn.commit()
        conn.close()
        return {"message": "Bill has been deleted"}

    # TODO implement edit bill
    def update_bill(self, id: str, edited_bill: Bill) -> Bill:
        conn = sqlite3.connect("bill.db")

        # create cursor
        c = conn.cursor()

        c.execute("UPDATE bills SET name=?, amount=?, due_date=? WHERE id = ? ",
                    [edited_bill.name, dollars_to_cents(edited_bill.amount), edited_bill.due_date, edited_bill.id])

        conn.commit()
        conn.close()
        return deserialize_row(Bill, self.get_bill_by_id(id), todays_date)


# Other functions
def get_largest_rowid() -> int:
    # connects to db we name,if it doesn't exist will create it
    conn = sqlite3.connect("bill.db")

    # create cursor
    c = conn.cursor()

    c.execute("SELECT * FROM bills ORDER BY id DESC LIMIT 1;")
    result: list[tuple[int]] = c.fetchall()
    conn.commit()
    conn.close()
    if result == []:
        return 0
    else:
        return result[0][0]



#check if tables are created, if not create them
#users table
conn = sqlite3.connect("bill.db")
c = conn.cursor()
data = c.execute('''
CREATE TABLE IF NOT EXISTS Users (user_id text, username text, password text, email text)
''')
conn.commit()
conn.close()
conn = sqlite3.connect("bill.db")


c = conn.cursor()
data = c.execute('''
CREATE TABLE IF NOT EXISTS bills (id text, name text, amount INTEGER, due_date text, user_id text)
''')
conn.commit()
conn.close()

