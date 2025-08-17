"""
Face service for managing known persons and face data
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.models.database_models import KnownPerson, FaceData
from backend.app.models.schemas import KnownPersonCreate, KnownPersonUpdate


class FaceService:
    """Service class for face recognition operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_known_person(self, person_data: KnownPersonCreate) -> KnownPerson:
        """Create a new known person"""
        db_person = KnownPerson(
            name=person_data.name,
            description=person_data.description,
            national_id=person_data.national_id,
            date_of_birth=person_data.date_of_birth,
            nationality=person_data.nationality,
            is_wanted=person_data.is_wanted,
            risk_level=person_data.risk_level,
            watch_list_category=person_data.watch_list_category
        )
        
        self.db.add(db_person)
        self.db.commit()
        self.db.refresh(db_person)
        
        return db_person
    
    def get_known_person_by_id(self, person_id: int) -> Optional[KnownPerson]:
        """Get known person by ID"""
        return self.db.query(KnownPerson).filter(KnownPerson.id == person_id).first()
    
    def get_known_person_by_name(self, name: str) -> Optional[KnownPerson]:
        """Get known person by name"""
        return self.db.query(KnownPerson).filter(KnownPerson.name == name).first()
    
    def get_all_known_persons(self) -> List[KnownPerson]:
        """Get all known persons"""
        return self.db.query(KnownPerson).order_by(KnownPerson.name).all()
    
    def get_wanted_persons(self) -> List[KnownPerson]:
        """Get all wanted persons"""
        return self.db.query(KnownPerson)\
                     .filter(KnownPerson.is_wanted == True)\
                     .order_by(desc(KnownPerson.risk_level))\
                     .all()
    
    def update_known_person(self, person_id: int, person_data: KnownPersonUpdate) -> Optional[KnownPerson]:
        """Update known person information"""
        person = self.get_known_person_by_id(person_id)
        if not person:
            return None
        
        if person_data.name is not None:
            person.name = person_data.name
        if person_data.description is not None:
            person.description = person_data.description
        if person_data.is_wanted is not None:
            person.is_wanted = person_data.is_wanted
        if person_data.risk_level is not None:
            person.risk_level = person_data.risk_level
        if person_data.watch_list_category is not None:
            person.watch_list_category = person_data.watch_list_category
        
        self.db.commit()
        self.db.refresh(person)
        
        return person
    
    def delete_known_person(self, person_id: int) -> bool:
        """Delete a known person"""
        person = self.get_known_person_by_id(person_id)
        if not person:
            return False
        
        # Delete related face data first
        self.db.query(FaceData).filter(FaceData.matched_person_id == person_id).delete()
        
        # Delete person
        self.db.delete(person)
        self.db.commit()
        
        return True
    
    def create_face_data(self, detection_id: int, face_encoding: str, 
                        landmarks: str, quality_score: float,
                        matched_person_id: Optional[int] = None,
                        match_confidence: Optional[float] = None) -> FaceData:
        """Create face data record"""
        db_face_data = FaceData(
            detection_id=detection_id,
            face_encoding=face_encoding,
            face_landmarks=landmarks,
            face_quality_score=quality_score,
            matched_person_id=matched_person_id,
            match_confidence=match_confidence
        )
        
        self.db.add(db_face_data)
        self.db.commit()
        self.db.refresh(db_face_data)
        
        return db_face_data
    
    def get_face_data_by_detection_id(self, detection_id: int) -> Optional[FaceData]:
        """Get face data by detection ID"""
        return self.db.query(FaceData).filter(FaceData.detection_id == detection_id).first()
    
    def get_face_matches_for_person(self, person_id: int) -> List[FaceData]:
        """Get all face matches for a person"""
        return self.db.query(FaceData)\
                     .filter(FaceData.matched_person_id == person_id)\
                     .order_by(desc(FaceData.created_at))\
                     .all()
    
    def search_persons_by_name(self, name_query: str) -> List[KnownPerson]:
        """Search persons by name"""
        return self.db.query(KnownPerson)\
                     .filter(KnownPerson.name.ilike(f"%{name_query}%"))\
                     .order_by(KnownPerson.name)\
                     .all()
    
    def get_persons_by_risk_level(self, risk_level: str) -> List[KnownPerson]:
        """Get persons by risk level"""
        return self.db.query(KnownPerson)\
                     .filter(KnownPerson.risk_level == risk_level)\
                     .order_by(KnownPerson.name)\
                     .all()
    
    def update_person_external_ids(self, person_id: int, 
                                  police_db_id: Optional[str] = None,
                                  interpol_db_id: Optional[str] = None) -> Optional[KnownPerson]:
        """Update external database IDs for a person"""
        person = self.get_known_person_by_id(person_id)
        if not person:
            return None
        
        if police_db_id is not None:
            person.police_db_id = police_db_id
        if interpol_db_id is not None:
            person.interpol_db_id = interpol_db_id
        
        self.db.commit()
        self.db.refresh(person)
        
        return person