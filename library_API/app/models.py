from sqlalchemy import Boolean, Column, Integer, Date, Float, Text
from database import Base


class BookDataModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Text)
    title = Column(Text)
    series = Column(Boolean)
    volume = Column(Integer)
    author = Column(Text)
    publisher = Column(Text)
    price = Column(Float)
    isbn = Column(Integer)
    wishlist = Column(Boolean)
    gift = Column(Boolean)
    borrow = Column(Boolean)
    releaseDate = Column(Date)
    payDate = Column(Date)
    startDate = Column(Date)
    endDate = Column(Date)
