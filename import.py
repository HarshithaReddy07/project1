import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine= create_engine("postgres://jxzosipnydmabf:902838b9e9d4bba2bab657bd563fa688b5e8ca54169194aa4b879cb31378370a@ec2-50-17-21-170.compute-1.amazonaws.com:5432/ddvff1uqkmtiop")
db =scoped_session(sessionmaker(bind=engine))

def main():
    # db.execute("CREATE TABLE login (username VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    # db.execute("CREATE TABLE review (isbn VARCHAR NOT NULL,username VARCHAR NOT NULL, rating INTEGER NOT NULL,review VARCHAR NOT NULL)")
    # db.execute("CREATE TABLE books (year VARCHAR NOT NULL ,title VARCHAR NOT NULL,author VARCHAR NOT NULL,isbn VARCHAR NOT NULL)")
    f=open("books.csv")
    reader =csv.reader(f)
    for isbn,title,author,year in reader:   
        db.execute("INSERT INTO books (year, title, author, isbn) VALUES (:year,:title,:author,:year)",{"year":year,"title":title,"author":author,"isbn":isbn})
        
    print("Done")            
    db.commit()    


if __name__ == "__main__":
    main()