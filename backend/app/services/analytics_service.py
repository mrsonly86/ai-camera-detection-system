"""
Analytics service for generating statistics and reports
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from backend.app.models.database_models import (
    DetectionSession, Detection, Alert, User, KnownPerson
)


class AnalyticsService:
    """Service class for analytics and statistics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_dashboard_stats(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        
        # Basic counts
        total_sessions = self.db.query(DetectionSession)\
                               .filter(DetectionSession.user_id == user_id)\
                               .filter(DetectionSession.created_at.between(start_date, end_date))\
                               .count()
        
        total_detections = self.db.query(Detection)\
                                 .join(DetectionSession)\
                                 .filter(DetectionSession.user_id == user_id)\
                                 .filter(Detection.timestamp.between(start_date, end_date))\
                                 .count()
        
        person_detections = self.db.query(Detection)\
                                  .join(DetectionSession)\
                                  .filter(DetectionSession.user_id == user_id)\
                                  .filter(Detection.object_class == 'person')\
                                  .filter(Detection.timestamp.between(start_date, end_date))\
                                  .count()
        
        alert_count = self.db.query(Detection)\
                            .join(DetectionSession)\
                            .filter(DetectionSession.user_id == user_id)\
                            .filter(Detection.is_alert == True)\
                            .filter(Detection.timestamp.between(start_date, end_date))\
                            .count()
        
        # Gender distribution
        gender_stats = self.db.query(Detection.gender, func.count(Detection.id))\
                             .join(DetectionSession)\
                             .filter(DetectionSession.user_id == user_id)\
                             .filter(Detection.object_class == 'person')\
                             .filter(Detection.timestamp.between(start_date, end_date))\
                             .group_by(Detection.gender)\
                             .all()
        
        gender_distribution = {gender: count for gender, count in gender_stats if gender}
        
        # Age statistics
        age_stats = self.db.query(
            func.avg(Detection.estimated_age),
            func.min(Detection.estimated_age),
            func.max(Detection.estimated_age)
        ).join(DetectionSession)\
         .filter(DetectionSession.user_id == user_id)\
         .filter(Detection.object_class == 'person')\
         .filter(Detection.estimated_age.isnot(None))\
         .filter(Detection.timestamp.between(start_date, end_date))\
         .first()
        
        avg_age, min_age, max_age = age_stats if age_stats[0] else (None, None, None)
        
        return {
            "summary": {
                "total_sessions": total_sessions,
                "total_detections": total_detections,
                "person_detections": person_detections,
                "alert_count": alert_count,
                "detection_rate": round(total_detections / max(total_sessions, 1), 2)
            },
            "gender_distribution": gender_distribution,
            "age_statistics": {
                "average_age": round(avg_age, 1) if avg_age else None,
                "min_age": min_age,
                "max_age": max_age
            }
        }
    
    def get_detection_timeline(self, user_id: int, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get hourly detection timeline"""
        
        # Group detections by hour
        timeline_data = self.db.query(
            func.date_trunc('hour', Detection.timestamp).label('hour'),
            func.count(Detection.id).label('detection_count'),
            func.count(func.distinct(func.case([(Detection.object_class == 'person', Detection.id)]))).label('person_count')
        ).join(DetectionSession)\
         .filter(DetectionSession.user_id == user_id)\
         .filter(Detection.timestamp.between(start_date, end_date))\
         .group_by(func.date_trunc('hour', Detection.timestamp))\
         .order_by(func.date_trunc('hour', Detection.timestamp))\
         .all()
        
        timeline = []
        for hour, detection_count, person_count in timeline_data:
            timeline.append({
                "timestamp": hour.isoformat(),
                "detections": detection_count,
                "persons": person_count
            })
        
        return timeline
    
    def get_gender_distribution(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get gender distribution statistics"""
        
        gender_stats = self.db.query(Detection.gender, func.count(Detection.id))\
                             .join(DetectionSession)\
                             .filter(DetectionSession.user_id == user_id)\
                             .filter(Detection.object_class == 'person')\
                             .filter(Detection.timestamp.between(start_date, end_date))\
                             .group_by(Detection.gender)\
                             .all()
        
        distribution = {"male": 0, "female": 0, "unknown": 0}
        for gender, count in gender_stats:
            if gender in distribution:
                distribution[gender] = count
            else:
                distribution["unknown"] += count
        
        return distribution
    
    def get_age_distribution(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get age distribution by ranges"""
        
        age_ranges = [
            ("0-17", 0, 17),
            ("18-25", 18, 25),
            ("26-35", 26, 35),
            ("36-45", 36, 45),
            ("46-55", 46, 55),
            ("56-65", 56, 65),
            ("66+", 66, 150)
        ]
        
        distribution = {}
        
        for range_name, min_age, max_age in age_ranges:
            count = self.db.query(Detection)\
                          .join(DetectionSession)\
                          .filter(DetectionSession.user_id == user_id)\
                          .filter(Detection.object_class == 'person')\
                          .filter(Detection.estimated_age.between(min_age, max_age))\
                          .filter(Detection.timestamp.between(start_date, end_date))\
                          .count()
            distribution[range_name] = count
        
        return distribution
    
    def get_alerts_summary(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get alerts summary"""
        
        total_alerts = self.db.query(Detection)\
                             .join(DetectionSession)\
                             .filter(DetectionSession.user_id == user_id)\
                             .filter(Detection.is_alert == True)\
                             .filter(Detection.timestamp.between(start_date, end_date))\
                             .count()
        
        # Recent alerts
        recent_alerts = self.db.query(Detection)\
                              .join(DetectionSession)\
                              .filter(DetectionSession.user_id == user_id)\
                              .filter(Detection.is_alert == True)\
                              .filter(Detection.timestamp.between(start_date, end_date))\
                              .order_by(desc(Detection.timestamp))\
                              .limit(10)\
                              .all()
        
        alert_reasons = self.db.query(Detection.alert_reason, func.count(Detection.id))\
                              .join(DetectionSession)\
                              .filter(DetectionSession.user_id == user_id)\
                              .filter(Detection.is_alert == True)\
                              .filter(Detection.timestamp.between(start_date, end_date))\
                              .group_by(Detection.alert_reason)\
                              .all()
        
        return {
            "total_alerts": total_alerts,
            "recent_alerts": [
                {
                    "id": alert.id,
                    "timestamp": alert.timestamp.isoformat(),
                    "reason": alert.alert_reason,
                    "confidence": alert.confidence
                } for alert in recent_alerts
            ],
            "alert_reasons": {reason: count for reason, count in alert_reasons if reason}
        }
    
    def get_session_performance(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific session"""
        
        session = self.db.query(DetectionSession).filter(DetectionSession.id == session_id).first()
        if not session:
            return None
        
        detections = self.db.query(Detection).filter(Detection.session_id == session_id).all()
        
        if not detections:
            return {
                "session_id": session_id,
                "session_name": session.session_name,
                "duration_minutes": 0,
                "total_detections": 0,
                "detections_per_minute": 0,
                "average_confidence": 0
            }
        
        # Calculate duration
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds() / 60
        else:
            duration = (datetime.utcnow() - session.start_time).total_seconds() / 60
        
        # Calculate metrics
        total_detections = len(detections)
        detections_per_minute = total_detections / max(duration, 1)
        avg_confidence = sum(d.confidence for d in detections) / total_detections
        
        person_detections = [d for d in detections if d.object_class == 'person']
        alerts = [d for d in detections if d.is_alert]
        
        return {
            "session_id": session_id,
            "session_name": session.session_name,
            "duration_minutes": round(duration, 2),
            "total_detections": total_detections,
            "person_detections": len(person_detections),
            "alerts": len(alerts),
            "detections_per_minute": round(detections_per_minute, 2),
            "average_confidence": round(avg_confidence, 3)
        }
    
    def export_user_data(self, user_id: int, start_date: datetime, end_date: datetime, format: str) -> Any:
        """Export user data in specified format"""
        
        # Get all detections in period
        detections = self.db.query(Detection)\
                           .join(DetectionSession)\
                           .filter(DetectionSession.user_id == user_id)\
                           .filter(Detection.timestamp.between(start_date, end_date))\
                           .order_by(Detection.timestamp)\
                           .all()
        
        if format == "json":
            return [
                {
                    "id": d.id,
                    "timestamp": d.timestamp.isoformat(),
                    "object_class": d.object_class,
                    "confidence": d.confidence,
                    "bbox": {
                        "x1": d.bbox_x1,
                        "y1": d.bbox_y1,
                        "x2": d.bbox_x2,
                        "y2": d.bbox_y2
                    },
                    "gender": d.gender,
                    "estimated_age": d.estimated_age,
                    "estimated_height": d.estimated_height,
                    "estimated_weight": d.estimated_weight,
                    "is_alert": d.is_alert,
                    "alert_reason": d.alert_reason
                } for d in detections
            ]
        
        elif format == "csv":
            # Return CSV headers and rows
            headers = [
                "id", "timestamp", "object_class", "confidence",
                "bbox_x1", "bbox_y1", "bbox_x2", "bbox_y2",
                "gender", "estimated_age", "estimated_height", "estimated_weight",
                "is_alert", "alert_reason"
            ]
            
            rows = []
            for d in detections:
                rows.append([
                    d.id, d.timestamp.isoformat(), d.object_class, d.confidence,
                    d.bbox_x1, d.bbox_y1, d.bbox_x2, d.bbox_y2,
                    d.gender, d.estimated_age, d.estimated_height, d.estimated_weight,
                    d.is_alert, d.alert_reason
                ])
            
            return {"headers": headers, "rows": rows}
        
        return []