from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from app.core.database import db
from app.routes.auth import get_current_user
from app.core.rbac import require_capability
from app.core.utils import validate_object_id, sanitize_error_message
from app.routes.audit import log_audit_event
from bson import ObjectId
from typing import List, Dict, Any, Union, Optional
from datetime import date, datetime, time
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import os
from app.core.logger import logger
from pathlib import Path
from app.ephy.index import EphyIndex
from app.core.config import EPHY_STORAGE_PATH
from app.core import config

router = APIRouter(tags=["Parcels"])

# Pydantic model for creating a parcel
GeoJsonOrCoords = Union[Dict[str, Any], List[List[List[float]]]]

class ParcelCreate(BaseModel):
    name: str
    crop_type: str
    area_ha: float
    establishment_id: str
    coordinates: GeoJsonOrCoords | None = None  # GeoJSON dict or polygon coordinates [[[lng, lat], ...]]
    planting_year: Optional[int] = None

class TreatmentCreate(BaseModel):
    data_tratament: date
    tip_tratament: str
    produs_utilizat: str
    amm: Optional[str] = None  # AMM number for auto-complete
    doza_aplicata: float  # dose per ha
    suprafata_tratata: Optional[float] = None  # area treated in ha
    operator: Optional[str] = None
    note_optionale: Optional[str] = None
    # Auto-filled from e-Phy
    znt_aquatique: Optional[int] = None
    znt_arthropodes: Optional[int] = None
    znt_plantes: Optional[int] = None
    dar_jour: Optional[int] = None
    max_applications: Optional[int] = None

class ParcelOut(BaseModel):
    id: str
    name: str
    crop_type: str
    area_ha: float
    establishment_id: str
    user_id: str
    planting_year: Optional[int] = None
    coordinates: Optional[GeoJsonOrCoords] = None
    created_at: Optional[str] = None

class TreatmentOut(BaseModel):
    id: str
    parcel_id: str
    data_tratament: Optional[str] = None
    tip_tratament: str
    produs_utilizat: str
    amm: Optional[str] = None
    doza_aplicata: float
    suprafata_tratata: Optional[float] = None
    cantitate_utilizata: Optional[float] = None
    operator: Optional[str] = None
    note_optionale: Optional[str] = None
    znt_aquatique: Optional[int] = None
    znt_arthropodes: Optional[int] = None
    znt_plantes: Optional[int] = None
    dar_jour: Optional[int] = None
    max_applications: Optional[int] = None
    created_at: Optional[str] = None

# Route POST /parcels - create a new parcel
@router.post(
    "/parcels",
    summary="Creează o parcelă nouă",
    response_model=ParcelOut,
    responses={
        201: {"description": "Parcelă creată"},
        400: {"description": "Date invalide"},
        403: {"description": "Acces interzis"}
    },
    status_code=201
)
async def create_parcel(
    data: ParcelCreate,
    user: dict = Depends(require_capability("parcel:create"))
):
    try:
        # Extract user_id from token
        user_id = user.get("sub")
        
        # Validate: check that establishment exists and belongs to user
        establishment_oid = validate_object_id(data.establishment_id, "establishment_id")
        establishment = await db["establishments"].find_one({
            "_id": establishment_oid,
            "user_id": user_id
        })
        
        if not establishment:
            raise HTTPException(status_code=403, detail="Establishment not found or access denied")
        
        if data.area_ha <= 0:
            raise HTTPException(status_code=400, detail="La surface doit être > 0")

        if data.planting_year is not None:
            current_year = datetime.utcnow().year
            if data.planting_year < 1900 or data.planting_year > current_year:
                raise HTTPException(status_code=400, detail="L'année de plantation est invalide")

        coordinates = data.coordinates
        if not coordinates:
            raise HTTPException(status_code=400, detail="Les coordonnées sont requises")

        if isinstance(coordinates, list):
            if not coordinates or not isinstance(coordinates[0], list) or len(coordinates[0]) < 3:
                raise HTTPException(status_code=400, detail="Invalid polygon coordinates")
            coordinates = {"type": "Polygon", "coordinates": coordinates}
        elif isinstance(coordinates, dict):
            if "type" not in coordinates or "coordinates" not in coordinates:
                raise HTTPException(status_code=400, detail="Invalid coordinates format")
        else:
            raise HTTPException(status_code=400, detail="Invalid coordinates format")

        # Create the parcel
        parcel = {
            "name": data.name,
            "crop_type": data.crop_type,
            "area_ha": data.area_ha,
            "establishment_id": data.establishment_id,
            "user_id": user_id,
            "coordinates": coordinates,  # GeoJSON coordinates
            "planting_year": data.planting_year,
            "created_at": datetime.utcnow()
        }
        
        # Save to MongoDB
        result = await db["parcels"].insert_one(parcel)

        await log_audit_event(
            user_id=user_id,
            action="parcel.create",
            outcome="success",
            resource_type="parcel",
            resource_id=str(result.inserted_id),
            details={"establishment_id": data.establishment_id}
        )
        
        return {
            "id": str(result.inserted_id),
            "name": data.name,
            "crop_type": data.crop_type,
            "area_ha": data.area_ha,
            "establishment_id": data.establishment_id,
            "user_id": user_id,
            "planting_year": data.planting_year,
            "created_at": parcel["created_at"].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating parcel: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

@router.get(
    "/parcels",
    summary="Listează toate parcelele utilizatorului",
    response_model=List[ParcelOut],
    responses={
        200: {"description": "Listă de parcele"},
        401: {"description": "Neautorizat"}
    }
)
async def list_parcels(
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(require_capability("parcel:view"))
):
    try:
        user_id = user.get("sub")

        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        cursor = db["parcels"].find({"user_id": user_id}).skip(offset).limit(limit)
        parcels = await cursor.to_list(length=limit)

        result = []
        for parcel in parcels:
            result.append({
                "id": str(parcel["_id"]),
                "name": parcel.get("name"),
                "crop_type": parcel.get("crop_type"),
                "area_ha": parcel.get("area_ha"),
                "establishment_id": parcel.get("establishment_id"),
                "user_id": parcel.get("user_id"),
                "coordinates": parcel.get("coordinates"),
                "planting_year": parcel.get("planting_year"),
                "created_at": parcel.get("created_at").isoformat() if parcel.get("created_at") else None
            })

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error listing parcels: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

# Route GET /parcels/by-establishment/{id} - MUST come before /{parcel_id} to avoid route conflicts
@router.get(
    "/parcels/by-establishment/{establishment_id}",
    summary="Listează parcelele unei exploatații",
    response_model=List[ParcelOut]
)
async def get_parcels_by_establishment(
    establishment_id: str,
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(require_capability("parcel:view"))
):
    try:
        # Extract user_id from token
        user_id = user.get("sub")
        
        # Validate: check that establishment exists and belongs to user
        establishment_oid = validate_object_id(establishment_id, "establishment_id")
        establishment = await db["establishments"].find_one({
            "_id": establishment_oid,
            "user_id": user_id
        })
        
        if not establishment:
            raise HTTPException(status_code=403, detail="Establishment not found or access denied")
        
        # Guardrails for pagination
        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        # Find parcels for this establishment with pagination
        cursor = db["parcels"].find({
            "establishment_id": establishment_id,
            "user_id": user_id
        }).skip(offset).limit(limit)
        parcels = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for each parcel
        result = []
        for parcel in parcels:
            result.append({
                "id": str(parcel["_id"]),
                "name": parcel.get("name"),
                "crop_type": parcel.get("crop_type"),
                "area_ha": parcel.get("area_ha"),
                "establishment_id": parcel.get("establishment_id"),
                "user_id": parcel.get("user_id"),
                "coordinates": parcel.get("coordinates"),  # Include GeoJSON coordinates
                "planting_year": parcel.get("planting_year"),
                "created_at": parcel.get("created_at").isoformat() if parcel.get("created_at") else None
            })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving parcels: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

# Route GET /parcels/{parcel_id} - get a single parcel by ID
@router.get(
    "/parcels/{parcel_id}",
    summary="Detalii parcelă",
    response_model=ParcelOut
)
async def get_parcel(
    parcel_id: str,
    user: dict = Depends(require_capability("parcel:view"))
):
    try:
        # Extract user_id from token
        user_id = user.get("sub")
        
        # Validate parcel_id format
        parcel_oid = validate_object_id(parcel_id, "parcel_id")
        
        # Find parcel and verify it belongs to user
        parcel = await db["parcels"].find_one({
            "_id": parcel_oid,
            "user_id": user_id
        })
        
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found")
        
        return {
            "id": str(parcel["_id"]),
            "name": parcel.get("name"),
            "crop_type": parcel.get("crop_type"),
            "area_ha": parcel.get("area_ha"),
            "establishment_id": parcel.get("establishment_id"),
            "user_id": parcel.get("user_id"),
            "coordinates": parcel.get("coordinates"),
            "planting_year": parcel.get("planting_year"),
            "created_at": parcel.get("created_at").isoformat() if parcel.get("created_at") else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error fetching parcel: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

def _validate_treatment_input(data: TreatmentCreate):
    if data.data_tratament > date.today():
        raise HTTPException(status_code=400, detail="La date du traitement ne peut pas être dans le futur")
    if data.doza_aplicata <= 0:
        raise HTTPException(status_code=400, detail="La dose appliquée doit être supérieure à 0")
    if not data.produs_utilizat or not data.produs_utilizat.strip():
        raise HTTPException(status_code=400, detail="Le produit utilisé est obligatoire")
    if config.TREATMENT_PRODUCTS and data.produs_utilizat not in config.TREATMENT_PRODUCTS:
        if not config.ALLOW_CUSTOM_TREATMENT_PRODUCTS:
            raise HTTPException(status_code=400, detail="Le produit utilisé n'est pas dans la liste autorisée")

async def _get_parcel_or_404(parcel_id: str, user_id: str):
    parcel_oid = validate_object_id(parcel_id, "parcel_id")
    parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user_id})
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found or access denied")
    return parcel

@router.get(
    "/parcels/{parcel_id}/treatments",
    summary="Listează tratamentele unei parcele",
    response_model=List[TreatmentOut]
)
async def get_treatments(
    parcel_id: str,
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(require_capability("treatment:view"))
):
    try:
        user_id = user.get("sub")
        await _get_parcel_or_404(parcel_id, user_id)

        limit = max(1, min(limit, 200))
        offset = max(0, offset)

        cursor = db["treatments"].find({"parcel_id": parcel_id, "user_id": user_id})\
            .sort("data_tratament", -1)\
            .skip(offset).limit(limit)
        treatments = []
        async for t in cursor:
            treatments.append({
                "id": str(t["_id"]),
                "parcel_id": t.get("parcel_id"),
                "data_tratament": t.get("data_tratament").date().isoformat() if t.get("data_tratament") else None,
                "tip_tratament": t.get("tip_tratament"),
                "produs_utilizat": t.get("produs_utilizat"),
                "amm": t.get("amm"),
                "doza_aplicata": t.get("doza_aplicata"),
                "suprafata_tratata": t.get("suprafata_tratata"),
                "cantitate_utilizata": t.get("cantitate_utilizata"),
                "operator": t.get("operator"),
                "note_optionale": t.get("note_optionale"),
                "znt_aquatique": t.get("znt_aquatique"),
                "znt_arthropodes": t.get("znt_arthropodes"),
                "znt_plantes": t.get("znt_plantes"),
                "dar_jour": t.get("dar_jour"),
                "max_applications": t.get("max_applications"),
                "created_at": t.get("created_at").isoformat() if t.get("created_at") else None,
            })
        return treatments
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving treatments: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving treatments")

@router.post(
    "/parcels/{parcel_id}/treatments",
    summary="Adaugă tratament",
    response_model=TreatmentOut,
    responses={
        201: {"description": "Tratament creat"},
        400: {"description": "Date invalide"}
    },
    status_code=201
)
async def create_treatment(
    parcel_id: str,
    data: TreatmentCreate,
    user: dict = Depends(require_capability("treatment:create"))
):
    try:
        user_id = user.get("sub")
        parcel = await _get_parcel_or_404(parcel_id, user_id)
        _validate_treatment_input(data)

        # Calculate quantity used
        area_treated = data.suprafata_tratata or parcel.get("area_ha", 0)
        quantity_used = data.doza_aplicata * area_treated if area_treated else 0

        # Auto-fill from e-Phy if AMM provided
        ephy_data = {}
        if data.amm:
            try:
                index = EphyIndex(Path(EPHY_STORAGE_PATH))
                product = index.get_product(data.amm)
                if product:
                    # Get first usage for viticulture
                    usages = index.get_usages(data.amm, limit=1)
                    if usages:
                        usage = usages[0]
                        ephy_data = {
                            "amm": data.amm,
                            "znt_aquatique": usage.get("znt_aquatique"),
                            "znt_arthropodes": usage.get("znt_arthropodes"),
                            "znt_plantes": usage.get("znt_plantes"),
                            "dar_jour": usage.get("dar_jour"),
                            "max_applications": usage.get("max_apps")
                        }
            except Exception as e:
                logger.warning(f"Failed to fetch e-Phy data for AMM {data.amm}: {e}")

        treatment = {
            "parcel_id": parcel_id,
            "user_id": user_id,
            "data_tratament": datetime.combine(data.data_tratament, time.min),
            "tip_tratament": data.tip_tratament,
            "produs_utilizat": data.produs_utilizat,
            "amm": data.amm,
            "doza_aplicata": data.doza_aplicata,
            "suprafata_tratata": area_treated,
            "cantitate_utilizata": quantity_used,
            "operator": data.operator,
            "note_optionale": data.note_optionale,
            "znt_aquatique": ephy_data.get("znt_aquatique") or data.znt_aquatique,
            "znt_arthropodes": ephy_data.get("znt_arthropodes") or data.znt_arthropodes,
            "znt_plantes": ephy_data.get("znt_plantes") or data.znt_plantes,
            "dar_jour": ephy_data.get("dar_jour") or data.dar_jour,
            "max_applications": ephy_data.get("max_applications") or data.max_applications,
            "created_at": datetime.utcnow()
        }

        result = await db["treatments"].insert_one(treatment)

        await log_audit_event(
            user_id=user_id,
            action="treatment.create",
            outcome="success",
            resource_type="treatment",
            resource_id=str(result.inserted_id),
            details={"parcel_id": parcel_id}
        )
        return {
            "id": str(result.inserted_id),
            "parcel_id": parcel_id,
            "data_tratament": data.data_tratament.isoformat(),
            "tip_tratament": data.tip_tratament,
            "produs_utilizat": data.produs_utilizat,
            "amm": data.amm,
            "doza_aplicata": data.doza_aplicata,
            "suprafata_tratata": area_treated,
            "cantitate_utilizata": quantity_used,
            "operator": data.operator,
            "note_optionale": data.note_optionale,
            "znt_aquatique": treatment.get("znt_aquatique"),
            "znt_arthropodes": treatment.get("znt_arthropodes"),
            "znt_plantes": treatment.get("znt_plantes"),
            "dar_jour": treatment.get("dar_jour"),
            "max_applications": treatment.get("max_applications"),
            "created_at": treatment["created_at"].isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error creating treatment: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

def _draw_logos(c: canvas.Canvas, width: float, height: float):
    draaf_path = os.getenv("DRAAF_LOGO_PATH")
    company_path = os.getenv("COMPANY_LOGO_PATH")

    if draaf_path and os.path.exists(draaf_path):
        c.drawImage(ImageReader(draaf_path), 20 * mm, height - 30 * mm, width=25 * mm, height=20 * mm, preserveAspectRatio=True, mask='auto')
    else:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(20 * mm, height - 20 * mm, "DRAAF")

    if company_path and os.path.exists(company_path):
        c.drawImage(ImageReader(company_path), width - 45 * mm, height - 30 * mm, width=25 * mm, height=20 * mm, preserveAspectRatio=True, mask='auto')
    else:
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(width - 20 * mm, height - 20 * mm, os.getenv("COMPANY_NAME", "VitiScan"))

def _build_draaf_pdf(parcel: dict, treatments: List[dict], soi: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    _draw_logos(c, width, height)

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 35 * mm, "Raport Tratamente - DRAAF")

    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, height - 45 * mm, f"Parcelă: {parcel.get('name', '-')}")
    c.drawString(20 * mm, height - 52 * mm, f"Suprafață: {parcel.get('area_ha', parcel.get('surface_ha', '-'))} ha")
    c.drawString(20 * mm, height - 59 * mm, f"Soi: {soi}")

    table_data = [[
        "Parcelă (nume / suprafață / soi)",
        "Dată tratament",
        "Tip + produs",
        "Doză (L/ha)",
        "Operator"
    ]]

    if treatments:
        for t in treatments:
            table_data.append([
                f"{parcel.get('name', '-')}\n{parcel.get('area_ha', parcel.get('surface_ha', '-'))} ha\n{soi}",
                t.get("data_tratament", "-"),
                f"{t.get('tip_tratament', '-')}\n{t.get('produs_utilizat', '-')}",
                str(t.get("doza_aplicata", "-")),
                t.get("operator", "-") or "-"
            ])
    else:
        table_data.append([
            f"{parcel.get('name', '-')}\n{parcel.get('area_ha', parcel.get('surface_ha', '-'))} ha\n{soi}",
            "-",
            "-",
            "-",
            "-"
        ])

    table = Table(table_data, colWidths=[60 * mm, 28 * mm, 50 * mm, 25 * mm, 25 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    table.wrapOn(c, width - 40 * mm, height)
    table.drawOn(c, 20 * mm, height - 150 * mm)

    c.setFont("Helvetica", 9)
    export_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    c.drawString(20 * mm, 20 * mm, f"Semnătură digitală: VitiScan | Data export: {export_date}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@router.get(
    "/parcels/{parcel_id}/export",
    summary="Exportă PDF DRAAF pentru parcelă",
    responses={
        200: {"description": "Export reușit"},
        202: {"description": "Export în curs"},
        500: {"description": "Eroare internă"}
    }
)
async def export_parcel_draaf(
    parcel_id: str,
    user: dict = Depends(require_capability("pdf:export"))
):
    try:
        user_id = user.get("sub")
        parcel = await _get_parcel_or_404(parcel_id, user_id)

        crops = await db["crops"].find({"parcel_id": parcel_id, "user_id": user_id}).sort("created_at", -1).to_list(length=1)
        crop = crops[0] if crops else None
        soi = (crop.get("variety") if crop else None) or (crop.get("name") if crop else None) or parcel.get("crop_type") or "-"

        treatments_cursor = db["treatments"].find({"parcel_id": parcel_id, "user_id": user_id}).sort("data_tratament", 1)
        treatments_list = []
        async for t in treatments_cursor:
            treatments_list.append({
                "data_tratament": t.get("data_tratament").date().isoformat() if t.get("data_tratament") else "-",
                "tip_tratament": t.get("tip_tratament"),
                "produs_utilizat": t.get("produs_utilizat"),
                "doza_aplicata": t.get("doza_aplicata"),
                "operator": t.get("operator"),
            })

        pdf_buffer = _build_draaf_pdf(parcel, treatments_list, soi)
        filename = f"draaf_parcel_{parcel_id}.pdf"
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        return StreamingResponse(pdf_buffer, media_type="application/pdf", headers=headers)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error exporting DRAAF PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

# Route PUT /parcels/{parcel_id} - update a parcel
@router.put("/parcels/{parcel_id}")
async def update_parcel(
    parcel_id: str,
    updated_data: ParcelCreate,
    user: dict = Depends(require_capability("parcel:update"))
):
    try:
        user_id = user.get("sub")
        
        # Verify that parcel exists and belongs to user
        parcel_oid = validate_object_id(parcel_id, "parcel_id")
        parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user_id})
        
        if not parcel:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")
        
        update_dict = updated_data.dict()
        if "coordinates" in update_dict:
            coords = update_dict.get("coordinates")
            if isinstance(coords, list):
                update_dict["coordinates"] = {"type": "Polygon", "coordinates": coords}
            elif isinstance(coords, dict):
                if "type" not in coords or "coordinates" not in coords:
                    raise HTTPException(status_code=400, detail="Invalid coordinates format")

        # Update the parcel
        await db["parcels"].update_one(
            {"_id": parcel_oid},
            {"$set": update_dict}
        )

        await log_audit_event(
            user_id=user_id,
            action="parcel.update",
            outcome="success",
            resource_type="parcel",
            resource_id=str(parcel_oid)
        )

        updated_parcel = await db["parcels"].find_one({"_id": parcel_oid, "user_id": user_id})
        if not updated_parcel:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")

        return {
            "id": str(updated_parcel["_id"]),
            "name": updated_parcel.get("name"),
            "crop_type": updated_parcel.get("crop_type"),
            "area_ha": updated_parcel.get("area_ha"),
            "establishment_id": updated_parcel.get("establishment_id"),
            "user_id": updated_parcel.get("user_id"),
            "coordinates": updated_parcel.get("coordinates"),
            "created_at": updated_parcel.get("created_at").isoformat() if updated_parcel.get("created_at") else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error updating parcel: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))

# Route DELETE /parcels/{parcel_id} - delete a parcel
@router.delete("/parcels/{parcel_id}", status_code=204)
async def delete_parcel(
    parcel_id: str,
    user: dict = Depends(require_capability("parcel:delete"))
):
    try:
        user_id = user.get("sub")
        
        # Delete parcel only if it belongs to user
        parcel_oid = validate_object_id(parcel_id, "parcel_id")
        result = await db["parcels"].delete_one({"_id": parcel_oid, "user_id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Parcel not found or access denied")

        await log_audit_event(
            user_id=user_id,
            action="parcel.delete",
            outcome="success",
            resource_type="parcel",
            resource_id=str(parcel_oid)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting parcel: {str(e)}")
        raise HTTPException(status_code=500, detail=sanitize_error_message(e))
