from datetime import datetime, timezone
from sqlalchemy.orm import Session
from models import Invoice, LineItem, TaxEntry, Category, Vendor

def create_invoice(
    db: Session,
    invoice_data: dict,
    line_items_data: list[dict] = None,
    tax_entries_data: list[dict] = None,
    category_ids: list[str] = None
) -> Invoice:
    """
    Creates an Invoice along with its LineItems, TaxEntries, and maps Category IDs.
    """
    db_invoice = Invoice(**invoice_data)
    
    # Associate categories if provided
    if category_ids:
        categories = db.query(Category).filter(Category.id.in_(category_ids)).all()
        db_invoice.categories = categories
        
    # Append line items
    if line_items_data:
        for item in line_items_data:
            db_item = LineItem(**item)
            db_invoice.line_items.append(db_item)
            
    # Append tax entries
    if tax_entries_data:
        for tax in tax_entries_data:
            db_tax = TaxEntry(**tax)
            db_invoice.tax_entries.append(db_tax)
            
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def get_invoice(db: Session, invoice_id: str) -> Invoice:
    """
    Get a single invoice by ID, excluding soft-deleted ones.
    """
    return db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.deleted_at.is_(None)
    ).first()

def list_invoices(
    db: Session,
    vendor_id: str = None,
    date_from = None,
    date_to = None,
    search: str = None
) -> list[Invoice]:
    """
    List invoices filtering out soft-deleted ones.
    Supports filtering by vendor_id, date_from, date_to, and generic text search.
    """
    query = db.query(Invoice).filter(Invoice.deleted_at.is_(None))
    
    if vendor_id:
        query = query.filter(Invoice.vendor_id == vendor_id)
    if date_from:
        query = query.filter(Invoice.invoice_date >= date_from)
    if date_to:
        query = query.filter(Invoice.invoice_date <= date_to)
    if search:
        search_filter = f"%{search}%"
        # Left outer join with Vendor to search on vendor name as well
        query = query.join(Invoice.vendor, isouter=True).filter(
            (Invoice.invoice_number.ilike(search_filter)) |
            (Invoice.notes.ilike(search_filter)) |
            (Invoice.raw_text.ilike(search_filter)) |
            (Vendor.name.ilike(search_filter))
        )
        
    return query.order_by(Invoice.invoice_date.desc(), Invoice.created_at.desc()).all()

def update_invoice(db: Session, invoice_id: str, update_data: dict) -> Invoice:
    """
    Update basic properties of an active invoice.
    """
    db_invoice = get_invoice(db, invoice_id)
    if not db_invoice:
        return None
    for key, value in update_data.items():
        if hasattr(db_invoice, key):
            setattr(db_invoice, key, value)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

def delete_invoice(db: Session, invoice_id: str) -> bool:
    """
    Perform a soft delete by setting deleted_at to current UTC time.
    Returns True if invoice existed and was marked deleted, False otherwise.
    """
    db_invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.deleted_at.is_(None)
    ).first()
    
    if not db_invoice:
        return False
        
    db_invoice.deleted_at = datetime.now(timezone.utc)
    db.commit()
    return True
