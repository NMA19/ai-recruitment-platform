"""
Documents Routes
Handles ANEM registration dossier/document management
"""

from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.models import Document, User, DocumentType, DocumentStatus
from ...schemas.schemas import DocumentCreate, DocumentUpdate, DocumentResponse, DossierStatus
from ...core.security import get_current_active_user


router = APIRouter(prefix="/documents", tags=["Documents"])

# Required documents for ANEM registration
REQUIRED_DOCUMENTS = [
    {"type": DocumentType.CNI.value, "name_fr": "Carte Nationale d'Identité", "name_ar": "بطاقة التعريف الوطنية", "name_en": "National ID Card", "required": True},
    {"type": DocumentType.RESIDENCE.value, "name_fr": "Certificat de Résidence", "name_ar": "شهادة الإقامة", "name_en": "Residence Certificate", "required": True},
    {"type": DocumentType.PHOTO.value, "name_fr": "Photos d'identité", "name_ar": "صور شمسية", "name_en": "ID Photos", "required": True},
    {"type": DocumentType.DIPLOMA.value, "name_fr": "Diplômes/Certificats", "name_ar": "الشهادات والدبلومات", "name_en": "Diplomas/Certificates", "required": True},
    {"type": DocumentType.CV.value, "name_fr": "CV (Curriculum Vitae)", "name_ar": "السيرة الذاتية", "name_en": "Resume/CV", "required": True},
    {"type": DocumentType.BIRTH_CERTIFICATE.value, "name_fr": "Extrait de Naissance", "name_ar": "شهادة الميلاد", "name_en": "Birth Certificate", "required": False},
    {"type": DocumentType.MILITARY.value, "name_fr": "Situation Militaire", "name_ar": "الوضعية تجاه الخدمة الوطنية", "name_en": "Military Service Status", "required": False},
    {"type": DocumentType.WORK_CERTIFICATE.value, "name_fr": "Attestation de Travail", "name_ar": "شهادة العمل", "name_en": "Work Certificate", "required": False},
]


@router.get("/requirements")
def get_document_requirements():
    """Get list of required documents for ANEM registration"""
    return {
        "documents": REQUIRED_DOCUMENTS,
        "minimum_required": 5,  # CNI, residence, photo, diploma, CV
        "message_fr": "Pour compléter votre inscription ANEM, veuillez soumettre les documents suivants",
        "message_ar": "لإكمال تسجيلك في ANEM، يرجى تقديم الوثائق التالية",
        "message_en": "To complete your ANEM registration, please submit the following documents"
    }


@router.get("/my-dossier", response_model=DossierStatus)
def get_my_dossier(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's dossier status with all documents"""
    # Get all user's documents
    user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    
    # Create a map of document types to documents
    doc_map = {doc.document_type: doc for doc in user_docs}
    
    # Build complete document list (including missing required ones)
    all_documents = []
    for req_doc in REQUIRED_DOCUMENTS:
        if req_doc["type"] in doc_map:
            all_documents.append(doc_map[req_doc["type"]])
        else:
            # Create a placeholder for missing document
            placeholder = Document(
                id=0,
                user_id=current_user.id,
                document_type=req_doc["type"],
                status=DocumentStatus.NOT_SUBMITTED.value,
                created_at=datetime.utcnow()
            )
            all_documents.append(placeholder)
    
    # Calculate statistics
    required_types = [d["type"] for d in REQUIRED_DOCUMENTS if d["required"]]
    total_required = len(required_types)
    
    submitted = [d for d in user_docs if d.status != DocumentStatus.NOT_SUBMITTED.value]
    approved = [d for d in user_docs if d.status == DocumentStatus.APPROVED.value]
    pending = [d for d in user_docs if d.status == DocumentStatus.PENDING.value]
    rejected = [d for d in user_docs if d.status == DocumentStatus.REJECTED.value]
    
    # Check if required documents are approved
    approved_required = sum(1 for d in approved if d.document_type in required_types)
    is_complete = approved_required >= total_required
    can_apply = approved_required >= 3  # Minimum 3 required documents approved
    
    completion = (len(approved) / total_required * 100) if total_required > 0 else 0
    
    return DossierStatus(
        total_required=total_required,
        total_submitted=len(submitted),
        total_approved=len(approved),
        total_pending=len(pending),
        total_rejected=len(rejected),
        completion_percentage=min(completion, 100),
        documents=all_documents,
        is_complete=is_complete,
        can_apply=can_apply
    )


@router.post("", response_model=DocumentResponse)
def submit_document(
    document: DocumentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a document for ANEM registration"""
    # Validate document type
    valid_types = [d.value for d in DocumentType]
    if document.document_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid document type. Must be one of: {valid_types}")
    
    # Check if document already exists
    existing = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.document_type == document.document_type
    ).first()
    
    if existing:
        # Update existing document
        existing.file_name = document.file_name
        existing.file_url = document.file_url
        existing.status = DocumentStatus.PENDING.value
        existing.submitted_at = datetime.utcnow()
        existing.notes = None  # Clear previous rejection notes
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new document
    new_doc = Document(
        user_id=current_user.id,
        document_type=document.document_type,
        file_name=document.file_name,
        file_url=document.file_url,
        status=DocumentStatus.PENDING.value,
        submitted_at=datetime.utcnow()
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc


@router.get("", response_model=List[DocumentResponse])
def get_my_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents submitted by the current user"""
    documents = db.query(Document).filter(Document.user_id == current_user.id).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document (only if not yet approved)"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status == DocumentStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Cannot delete approved documents")
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}


# Admin routes for reviewing documents
@router.patch("/{document_id}/review", response_model=DocumentResponse)
def review_document(
    document_id: int,
    update: DocumentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Review and update document status (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validate status
    valid_statuses = [s.value for s in DocumentStatus]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    document.status = update.status
    document.notes = update.notes
    document.reviewed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return document


@router.get("/admin/pending", response_model=List[DocumentResponse])
def get_pending_documents(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all pending documents for review (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    documents = db.query(Document).filter(
        Document.status == DocumentStatus.PENDING.value
    ).order_by(Document.submitted_at.asc()).all()
    
    return documents
