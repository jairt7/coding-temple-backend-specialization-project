from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from typing import List
from datetime import date
from sqlalchemy import DECIMAL
from decimal import Decimal


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


service_mechanic = db.Table(
    'service_mechanic',
    db.metadata,
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_tickets.id', ondelete='CASCADE'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id', ondelete='CASCADE'), primary_key=True)
)

class Customer(Base):
    __tablename__ = 'customers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(100), nullable=False)

    service_tickets: Mapped[List['ServiceTicket']] = relationship(back_populates='customer')

class ServiceTicket(Base):
    __tablename__ = 'service_tickets'

    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(17), nullable=False)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(db.Text)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id', ondelete='CASCADE'))

    customer: Mapped['Customer'] = relationship(back_populates='service_tickets')
    mechanics: Mapped[List['Mechanic']] = relationship(secondary=service_mechanic, back_populates='service_tickets')
    service_inventory: Mapped[List['ServiceInventory']] = relationship(back_populates='service_ticket', cascade="all, delete-orphan")

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    email: Mapped[str] = mapped_column(db.String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), unique=True, nullable=False)
    salary: Mapped[float] = mapped_column(db.Numeric(10, 2), nullable=False)

    service_tickets: Mapped[List['ServiceTicket']] = relationship(secondary=service_mechanic, back_populates='mechanics')

class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)

    service_inventory: Mapped[List['ServiceInventory']] = relationship(back_populates='item', cascade="all, delete-orphan")
    
class ServiceInventory(Base):
    __tablename__ = 'service_inventory'

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id', ondelete='CASCADE'), nullable=False)
    item_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    service_ticket: Mapped['ServiceTicket'] = relationship(back_populates='service_inventory')
    item: Mapped['Inventory'] = relationship(back_populates='service_inventory')