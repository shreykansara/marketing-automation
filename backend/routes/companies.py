from fastapi import APIRouter
from data.db import companies_collection

router = APIRouter(prefix="/api/companies", tags=["companies"])

@router.get("")
def get_companies():
    # Fetch all companies from the database
    companies = list(companies_collection.find().sort("signals_count", -1))
    
    # Remove the internal MongoDB ObjectId before returning
    for company in companies:
        company.pop("_id", None)
        
    return {"data": companies}
