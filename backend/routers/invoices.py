from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from crud import invoices as invoices_crud

router = APIRouter(prefix="/invoices", tags=["invoices"])

# -------------------------------------------------------------
# Pydantic Schemas (DTOs)
# -------------------------------------------------------------

class CategorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    color: str

class VendorSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    gstin: Optional[str] = None
    pan: Optional[str] = None
    created_at: datetime

class LineItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    invoice_id: str
    description: str
    hsn_code: Optional[str] = None
    quantity: Decimal
    unit: Optional[str] = None
    unit_price: Decimal
    line_total: Decimal
    cgst_pct: Optional[Decimal] = None
    sgst_pct: Optional[Decimal] = None
    igst_pct: Optional[Decimal] = None

class TaxEntrySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    invoice_id: str
    tax_type: str
    rate: Decimal
    amount: Decimal

# Basic invoice schema for list view
class InvoiceListSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    subtotal: Decimal
    discount: Decimal
    tax_total: Decimal
    grand_total: Decimal
    currency: str
    file_path: str
    extraction_method: str
    created_at: datetime
    vendor: Optional[VendorSchema] = None
    categories: List[CategorySchema] = []

# Detailed invoice schema for single item get
class InvoiceDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    vendor_id: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    subtotal: Decimal
    discount: Decimal
    tax_total: Decimal
    grand_total: Decimal
    currency: str
    file_path: str
    extraction_method: str
    raw_text: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    vendor: Optional[VendorSchema] = None
    categories: List[CategorySchema] = []
    line_items: List[LineItemSchema] = []
    tax_entries: List[TaxEntrySchema] = []

# Request body schema for updating notes
class UpdateNotesRequest(BaseModel):
    notes: Optional[str] = None

# -------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------

@router.get("", response_model=List[InvoiceListSchema])
def get_invoices(
    vendor_id: Optional[str] = Query(None, description="Filter by Vendor ID"),
    date_from: Optional[date] = Query(None, description="Filter by invoice date from"),
    date_to: Optional[date] = Query(None, description="Filter by invoice date to"),
    search: Optional[str] = Query(None, description="Search text in invoice fields or vendor name"),
    db: Session = Depends(get_db)
):
    """
    List all active (non soft-deleted) invoices matching the query criteria.
    """
    return invoices_crud.list_invoices(
        db,
        vendor_id=vendor_id,
        date_from=date_from,
        date_to=date_to,
        search=search
    )

@router.get("/{id}", response_model=InvoiceDetailSchema)
def get_invoice_by_id(id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about an active invoice, including line items and taxes.
    """
    db_invoice = invoices_crud.get_invoice(db, id)
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return db_invoice

@router.delete("/{id}")
def delete_invoice_by_id(id: str, db: Session = Depends(get_db)):
    """
    Soft delete an invoice.
    """
    success = invoices_crud.delete_invoice(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found or already deleted"
        )
    return {"message": "Invoice successfully deleted", "id": id}

@router.patch("/{id}/notes", response_model=InvoiceDetailSchema)
def patch_invoice_notes(id: str, payload: UpdateNotesRequest, db: Session = Depends(get_db)):
    """
    Update notes for a specific invoice.
    """
    db_invoice = invoices_crud.update_invoice(db, id, {"notes": payload.notes})
    if not db_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return db_invoice
