"""
Cost ledger management for VitiScan v3
Tracks costs per kg/ha for vineyard operations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import db
from app.core.security import get_current_user
from app.core.tenancy import require_tenant
import csv
import io
import logging
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/costs", tags=["Costs"])

class CostEntry(BaseModel):
    """Cost entry model"""
    id: Optional[str] = None
    establishment_id: str
    parcel_id: Optional[str] = None
    crop_type: str
    cost_type: str  # e.g., "treatment", "labor", "equipment"
    description: str
    amount_eur: float
    quantity_kg: Optional[float] = None
    area_ha: Optional[float] = None
    date: datetime
    supplier: Optional[str] = None
    invoice_number: Optional[str] = None
    user_id: str
    created_at: datetime = datetime.utcnow()

class CostSummary(BaseModel):
    """Cost summary per kg/ha"""
    crop_type: str
    total_cost_eur: float
    total_area_ha: float
    cost_per_ha: float
    cost_per_kg: Optional[float] = None  # if quantity_kg available

@router.post("/entries", summary="Add cost entry")
async def add_cost_entry(
    entry: CostEntry,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant)
):
    """Add a new cost entry"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    if entry.establishment_id != establishment_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    entry.user_id = current_user["sub"]
    
    result = await db.cost_entries.insert_one(entry.dict())
    return {"id": str(result.inserted_id)}

@router.get("/entries", summary="List cost entries")
async def list_cost_entries(
    crop_type: Optional[str] = None,
    cost_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant)
) -> List[CostEntry]:
    """List cost entries with optional filters"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    query = {"establishment_id": establishment_id}
    
    if crop_type:
        query["crop_type"] = crop_type
    if cost_type:
        query["cost_type"] = cost_type
    if start_date or end_date:
        date_query = {}
        if start_date:
            date_query["$gte"] = start_date
        if end_date:
            date_query["$lte"] = end_date
        query["date"] = date_query
    
    entries = await db.cost_entries.find(query).to_list(None)
    return [CostEntry(**entry) for entry in entries]

@router.get("/summary", summary="Cost summary per kg/ha")
async def get_cost_summary(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant)
) -> List[CostSummary]:
    """Get cost summary aggregated by crop type"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    pipeline = [
        {"$match": {"establishment_id": establishment_id}},
        {"$group": {
            "_id": "$crop_type",
            "total_cost_eur": {"$sum": "$amount_eur"},
            "total_area_ha": {"$sum": "$area_ha"},
            "total_quantity_kg": {"$sum": "$quantity_kg"}
        }},
        {"$project": {
            "crop_type": "$_id",
            "total_cost_eur": 1,
            "total_area_ha": 1,
            "cost_per_ha": {"$divide": ["$total_cost_eur", "$total_area_ha"]},
            "cost_per_kg": {"$cond": {
                "if": {"$gt": ["$total_quantity_kg", 0]},
                "then": {"$divide": ["$total_cost_eur", "$total_quantity_kg"]},
                "else": None
            }}
        }}
    ]
    
    results = await db.cost_entries.aggregate(pipeline).to_list(None)
    return [CostSummary(**result) for result in results]

@router.post("/import-csv", summary="Import costs from CSV")
async def import_costs_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant)
):
    """Import cost entries from CSV file"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    csv_reader = csv.DictReader(io.StringIO(content.decode('utf-8')))
    
    entries = []
    for row in csv_reader:
        try:
            entry = CostEntry(
                establishment_id=establishment_id,
                parcel_id=row.get('parcel_id'),
                crop_type=row['crop_type'],
                cost_type=row['cost_type'],
                description=row['description'],
                amount_eur=float(row['amount_eur']),
                quantity_kg=float(row.get('quantity_kg', 0)) if row.get('quantity_kg') else None,
                area_ha=float(row.get('area_ha', 0)) if row.get('area_ha') else None,
                date=datetime.fromisoformat(row['date']),
                supplier=row.get('supplier'),
                invoice_number=row.get('invoice_number'),
                user_id=current_user["sub"]
            )
            entries.append(entry.dict())
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid row: {row}, error: {e}")
            continue
    
    if entries:
        await db.cost_entries.insert_many(entries)
    
    return {"imported": len(entries)}

@router.get("/export-csv", summary="Export costs to CSV")
async def export_costs_csv(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(require_tenant)
):
    """Export cost entries to CSV"""
    establishment_id = tenant_id.split(':')[1] if ':' in tenant_id else tenant_id
    
    entries = await db.cost_entries.find({"establishment_id": establishment_id}).to_list(None)
    
    def generate_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "establishment_id", "parcel_id", "crop_type", "cost_type", "description",
            "amount_eur", "quantity_kg", "area_ha", "date", "supplier", "invoice_number"
        ])
        
        # Write data
        for entry in entries:
            writer.writerow([
                entry.get("establishment_id"),
                entry.get("parcel_id"),
                entry.get("crop_type"),
                entry.get("cost_type"),
                entry.get("description"),
                entry.get("amount_eur"),
                entry.get("quantity_kg"),
                entry.get("area_ha"),
                entry.get("date").isoformat() if entry.get("date") else "",
                entry.get("supplier"),
                entry.get("invoice_number")
            ])
        
        output.seek(0)
        return output.getvalue()
    
    return StreamingResponse(
        io.StringIO(generate_csv()),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=costs.csv"}
    )