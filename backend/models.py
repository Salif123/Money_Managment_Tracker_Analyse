import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Numeric,
    Text,
    DateTime,
    Date,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import relationship

from database import Base

# Many-to-many helper table for Invoice and Category
invoice_categories = Table(
    "invoice_categories",
    Base.metadata,
    Column(
        "invoice_id",
        String(36),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "category_id",
        String(36),
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    gstin = Column(String, nullable=True)
    pan = Column(String, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    invoices = relationship("Invoice", back_populates="vendor")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=True)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0.0, nullable=False)
    tax_total = Column(Numeric(12, 2), default=0.0, nullable=False)
    grand_total = Column(Numeric(12, 2), nullable=False)
    currency = Column(String, default="INR", nullable=False)
    file_path = Column(String, nullable=False)
    extraction_method = Column(String, nullable=False)
    raw_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    vendor = relationship("Vendor", back_populates="invoices")
    line_items = relationship(
        "LineItem",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    tax_entries = relationship(
        "TaxEntry",
        back_populates="invoice",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    categories = relationship(
        "Category",
        secondary=invoice_categories,
        back_populates="invoices"
    )


class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(
        String(36),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False
    )
    description = Column(String, nullable=False)
    hsn_code = Column(String, nullable=True)
    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(String, nullable=True)
    unit_price = Column(Numeric(12, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    cgst_pct = Column(Numeric(5, 2), nullable=True)
    sgst_pct = Column(Numeric(5, 2), nullable=True)
    igst_pct = Column(Numeric(5, 2), nullable=True)

    # Relationships
    invoice = relationship("Invoice", back_populates="line_items")


class TaxEntry(Base):
    __tablename__ = "tax_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    invoice_id = Column(
        String(36),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False
    )
    tax_type = Column(String, nullable=False)  # "CGST" | "SGST" | "IGST" | "CESS" | "OTHER"
    rate = Column(Numeric(5, 2), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)

    # Relationships
    invoice = relationship("Invoice", back_populates="tax_entries")


class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    color = Column(String, default="#6366f1", nullable=False)

    # Relationships
    invoices = relationship(
        "Invoice",
        secondary=invoice_categories,
        back_populates="categories"
    )
