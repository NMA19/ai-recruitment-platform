"""
Profile routes for CV/Profile management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from typing import Optional, List

from ...db.database import get_db
from ...models.models import User
from ...schemas.schemas import ProfileUpdate, ProfileResponse, EducationEntry, ExperienceEntry, LanguageEntry
from ...core.security import get_current_user


router = APIRouter(prefix="/profile", tags=["Profile"])


def parse_json_field(field: Optional[str], entry_class):
    """Parse JSON string to list of entries"""
    if not field:
        return None
    try:
        data = json.loads(field)
        return [entry_class(**item) for item in data] if isinstance(data, list) else None
    except (json.JSONDecodeError, TypeError):
        return None


def serialize_json_field(data: Optional[List]) -> Optional[str]:
    """Serialize list of entries to JSON string"""
    if not data:
        return None
    return json.dumps([item.model_dump() for item in data])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        phone=current_user.phone,
        wilaya=current_user.wilaya,
        address=current_user.address,
        date_of_birth=current_user.date_of_birth,
        bio=current_user.bio,
        education=parse_json_field(current_user.education, EducationEntry),
        experience=parse_json_field(current_user.experience, ExperienceEntry),
        skills=current_user.skills,
        languages=parse_json_field(current_user.languages, LanguageEntry),
        anem_registered=current_user.anem_registered,
        anem_registration_date=current_user.anem_registration_date,
        anem_renewal_date=current_user.anem_renewal_date
    )


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    update_data = profile_data.model_dump(exclude_unset=True)
    
    # Handle JSON fields
    if "education" in update_data and update_data["education"] is not None:
        update_data["education"] = serialize_json_field(profile_data.education)
    if "experience" in update_data and update_data["experience"] is not None:
        update_data["experience"] = serialize_json_field(profile_data.experience)
    if "languages" in update_data and update_data["languages"] is not None:
        update_data["languages"] = serialize_json_field(profile_data.languages)
    
    # Update user fields
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        phone=current_user.phone,
        wilaya=current_user.wilaya,
        address=current_user.address,
        date_of_birth=current_user.date_of_birth,
        bio=current_user.bio,
        education=parse_json_field(current_user.education, EducationEntry),
        experience=parse_json_field(current_user.experience, ExperienceEntry),
        skills=current_user.skills,
        languages=parse_json_field(current_user.languages, LanguageEntry),
        anem_registered=current_user.anem_registered,
        anem_registration_date=current_user.anem_registration_date,
        anem_renewal_date=current_user.anem_renewal_date
    )


# Algerian Wilayas for validation
ALGERIAN_WILAYAS = [
    "Adrar", "Chlef", "Laghouat", "Oum El Bouaghi", "Batna", "Béjaïa", "Biskra",
    "Béchar", "Blida", "Bouira", "Tamanrasset", "Tébessa", "Tlemcen", "Tiaret",
    "Tizi Ouzou", "Alger", "Djelfa", "Jijel", "Sétif", "Saïda", "Skikda",
    "Sidi Bel Abbès", "Annaba", "Guelma", "Constantine", "Médéa", "Mostaganem",
    "M'Sila", "Mascara", "Ouargla", "Oran", "El Bayadh", "Illizi", "Bordj Bou Arréridj",
    "Boumerdès", "El Tarf", "Tindouf", "Tissemsilt", "El Oued", "Khenchela",
    "Souk Ahras", "Tipaza", "Mila", "Aïn Defla", "Naâma", "Aïn Témouchent",
    "Ghardaïa", "Relizane", "El M'Ghair", "El Meniaa", "Ouled Djellal",
    "Bordj Badji Mokhtar", "Béni Abbès", "Timimoun", "Touggourt", "Djanet",
    "In Salah", "In Guezzam"
]


@router.get("/wilayas")
async def get_wilayas():
    """Get list of Algerian Wilayas"""
    return {"wilayas": ALGERIAN_WILAYAS}
