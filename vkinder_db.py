from dotenv.main import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

# функция подключения к базе данных book
def connect_db():
    load_dotenv()
    password = os.environ['password']
    DSN = f'postgresql://postgres:{password}@localhost:5432/books'
    engine = sq.create_engine(DSN)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session, engine



Base = declarative_base()

class Publisher(Base):
    __tablename__ = 'publisher'

    id = sq.Column(sq.Integer, primary_key=True)
    pub_name = sq.Column(sq.Text, nullable=False)

class Book(Base):
    __tablename__ = 'book'

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.Text, nullable=False)
    pub_id = sq.Column(sq.Integer, sq.ForeignKey('publisher.id'))
    publisher = relationship(Publisher, backref='publisher')

class Shop(Base):
    __tablename__ = 'shop'

    id = sq.Column(sq.Integer, primary_key=True)
    shop_name = sq.Column(sq.Text)

class Stock(Base):
    __tablename__ = 'stock'

    id = sq.Column(sq.Integer, primary_key=True)
    book_id = sq.Column(sq.Integer, sq.ForeignKey('book.id'))
    shop_id = sq.Column(sq.Integer, sq.ForeignKey('shop.id'))
    count = sq.Column(sq.Integer)
    book = relationship(Book, backref='book')
    shop = relationship(Shop, backref='shop')

class Sale(Base):
    __tablename__ = 'sale'

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Numeric(10, 2), nullable=False)
    date_sale = sq.Column(sq.Date, nullable=False)
    stock_id = sq.Column(sq.Integer, sq.ForeignKey('stock.id'))
    count = sq.Column(sq.Integer, nullable=False)
    stock = relationship(Stock, backref='stock')

def create_tables(engine):
    Base.metadata.create_all(engine)