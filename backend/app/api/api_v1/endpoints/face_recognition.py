"""
Face recognition endpoints
"""
import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image
import cv2
import numpy as np

from backend.app.core.database import get_db
from backend.app.models.schemas import KnownPerson, KnownPersonCreate, KnownPersonUpdate
from backend.app.api.api_v1.endpoints.auth import get_current_user
from backend.app.services.face_service import FaceService
from backend.app.ai_engine.face_recognition import get_face_recognition

router = APIRouter()


@router.post("/known-persons", response_model=KnownPerson)
async def add_known_person(
    person_data: KnownPersonCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new known person to the database"""
    face_service = FaceService(db)
    person = face_service.create_known_person(person_data)
    return person


@router.get("/known-persons", response_model=List[KnownPerson])
async def get_known_persons(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all known persons"""
    face_service = FaceService(db)
    persons = face_service.get_all_known_persons()
    return persons


@router.get("/known-persons/{person_id}", response_model=KnownPerson)
async def get_known_person(
    person_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific known person"""
    face_service = FaceService(db)
    person = face_service.get_known_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/known-persons/{person_id}", response_model=KnownPerson)
async def update_known_person(
    person_id: int,
    person_data: KnownPersonUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a known person"""
    face_service = FaceService(db)
    person = face_service.update_known_person(person_id, person_data)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.delete("/known-persons/{person_id}")
async def delete_known_person(
    person_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a known person"""
    face_service = FaceService(db)
    success = face_service.delete_known_person(person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Person deleted successfully"}


@router.post("/known-persons/{person_id}/add-face")
async def add_face_to_person(
    person_id: int,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a face image to a known person"""
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Get person from database
        face_service = FaceService(db)
        person = face_service.get_known_person_by_id(person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        
        # Add face to recognition system
        face_recognition = get_face_recognition()
        success = face_recognition.add_known_face(
            image_np, 
            person.name,
            {
                'id': person.id,
                'name': person.name,
                'is_wanted': person.is_wanted,
                'risk_level': person.risk_level
            }
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Could not extract face from image")
        
        return {"message": "Face added successfully to person"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add face: {str(e)}")


@router.post("/recognize")
async def recognize_face(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Recognize a face from uploaded image"""
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Recognize face
        face_recognition = get_face_recognition()
        result = face_recognition.recognize_face(image_np)
        
        # Calculate quality metrics
        quality = face_recognition.calculate_face_quality(image_np)
        
        return {
            "recognition_result": result,
            "face_quality": quality,
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face recognition failed: {str(e)}")


@router.get("/system-stats")
async def get_face_recognition_stats(current_user = Depends(get_current_user)):
    """Get face recognition system statistics"""
    try:
        face_recognition = get_face_recognition()
        stats = face_recognition.get_statistics()
        
        # Get face list
        faces_list = face_recognition.get_known_faces_list()
        stats['known_faces'] = faces_list
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.post("/update-tolerance")
async def update_recognition_tolerance(
    tolerance: float,
    current_user = Depends(get_current_user)
):
    """Update face recognition tolerance"""
    try:
        if not 0.0 <= tolerance <= 1.0:
            raise HTTPException(status_code=400, detail="Tolerance must be between 0.0 and 1.0")
        
        face_recognition = get_face_recognition()
        face_recognition.update_tolerance(tolerance)
        
        return {"message": f"Tolerance updated to {tolerance}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update tolerance: {str(e)}")


@router.post("/calculate-quality")
async def calculate_face_quality(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Calculate quality metrics for a face image"""
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Calculate quality
        face_recognition = get_face_recognition()
        quality = face_recognition.calculate_face_quality(image_np)
        
        return {
            "filename": file.filename,
            "quality_metrics": quality
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality calculation failed: {str(e)}")