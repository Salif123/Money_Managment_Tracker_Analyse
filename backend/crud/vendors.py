from sqlalchemy.orm import Session
from models import Vendor

def create_or_get_vendor(
    db: Session,
    name: str,
    address: str = None,
    phone: str = None,
    email: str = None,
    gstin: str = None,
    pan: str = None,
) -> Vendor:
    """
    Retrieve vendor if it already exists by name, otherwise create a new one.
    Updates missing vendor profile fields if they are supplied.
    """
    stripped_name = name.strip()
    db_vendor = db.query(Vendor).filter(Vendor.name == stripped_name).first()
    
    if db_vendor:
        updated = False
        if address and not db_vendor.address:
            db_vendor.address = address
            updated = True
        if phone and not db_vendor.phone:
            db_vendor.phone = phone
            updated = True
        if email and not db_vendor.email:
            db_vendor.email = email
            updated = True
        if gstin and not db_vendor.gstin:
            db_vendor.gstin = gstin
            updated = True
        if pan and not db_vendor.pan:
            db_vendor.pan = pan
            updated = True
        
        if updated:
            db.commit()
            db.refresh(db_vendor)
        return db_vendor

    # Create new vendor if not exists
    db_vendor = Vendor(
        name=stripped_name,
        address=address,
        phone=phone,
        email=email,
        gstin=gstin,
        pan=pan,
    )
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def list_vendors(db: Session):
    """
    List all vendors ordered alphabetically by name.
    """
    return db.query(Vendor).order_by(Vendor.name).all()
