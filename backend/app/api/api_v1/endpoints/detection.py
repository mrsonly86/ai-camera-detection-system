"""
Detection endpoints for real-time object detection
"""
import io
import cv2
import numpy as np
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from PIL import Image

from backend.app.core.database import get_db
from backend.app.models.schemas import DetectionResult, DetectionSession, DetectionSessionCreate
from backend.app.api.api_v1.endpoints.auth import get_current_user
from backend.app.services.detection_service import DetectionService
from backend.app.ai_engine.yolo_detector import get_detector
from backend.app.ai_engine.advanced_analysis import get_analyzer
from backend.app.ai_engine.face_recognition import get_face_recognition
from backend.app.ai_engine.camera_interface import get_camera

router = APIRouter()


@router.post("/session", response_model=DetectionSession)
async def create_detection_session(
    session_data: DetectionSessionCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new detection session"""
    detection_service = DetectionService(db)
    session = detection_service.create_session(current_user.id, session_data)
    return session


@router.get("/sessions", response_model=List[DetectionSession])
async def get_detection_sessions(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's detection sessions"""
    detection_service = DetectionService(db)
    sessions = detection_service.get_user_sessions(current_user.id)
    return sessions


@router.post("/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    session_id: int = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze uploaded image for objects and faces"""
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Get AI engines
        detector = get_detector()
        analyzer = get_analyzer()
        face_recognition = get_face_recognition()
        
        # Detect objects
        detections = detector.detect(image_np)
        
        results = []
        for detection in detections:
            result = {
                'object_class': detection['class_name'],
                'confidence': detection['confidence'],
                'bbox': detection['bbox']
            }
            
            # If it's a person, do advanced analysis
            if detection['class_name'] == 'person':
                analysis = analyzer.analyze_person(image_np, detection['bbox'])
                result.update(analysis)
                
                # Extract face for recognition
                bbox = detection['bbox']
                x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
                face_region = image_np[y1:y1+int((y2-y1)*0.4), x1:x2]
                
                if face_region.size > 0:
                    face_result = face_recognition.recognize_face(face_region)
                    result['face_match'] = face_result
                    
                    quality = face_recognition.calculate_face_quality(face_region)
                    result['face_quality_score'] = quality['overall']
            
            results.append(result)
        
        # Save to database if session provided
        if session_id:
            detection_service = DetectionService(db)
            for result in results:
                detection_service.save_detection(session_id, result, str(file.filename))
        
        return {
            'filename': file.filename,
            'detections': results,
            'total_detections': len(results),
            'person_count': len([r for r in results if r['object_class'] == 'person'])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/live-stream")
async def live_stream():
    """Start live camera stream with detection"""
    def generate():
        camera = get_camera()
        detector = get_detector()
        
        try:
            while True:
                frame = camera.get_frame()
                if frame is None:
                    continue
                
                # Detect objects
                detections = detector.detect_persons(frame)
                
                # Draw bounding boxes
                for detection in detections:
                    bbox = detection['bbox']
                    x1, y1, x2, y2 = int(bbox['x1']), int(bbox['y1']), int(bbox['x2']), int(bbox['y2'])
                    
                    # Draw rectangle
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    
                    # Draw confidence
                    confidence_text = f"Person: {detection['confidence']:.2f}"
                    cv2.putText(frame, confidence_text, (x1, y1-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Encode frame
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        except Exception as e:
            print(f"Stream error: {e}")
    
    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.post("/start-live-detection")
async def start_live_detection(
    session_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start live detection with database recording"""
    try:
        camera = get_camera()
        detection_service = DetectionService(db)
        
        def detection_callback(frame):
            detector = get_detector()
            analyzer = get_analyzer()
            
            # Detect persons
            detections = detector.detect_persons(frame)
            
            # Analyze each person
            for detection in detections:
                analysis = analyzer.analyze_person(frame, detection['bbox'])
                
                # Combine detection and analysis results
                result = {
                    'object_class': detection['class_name'],
                    'confidence': detection['confidence'],
                    'bbox': detection['bbox'],
                    **analysis
                }
                
                # Save to database
                detection_service.save_detection(session_id, result)
        
        # Start camera with callback
        camera.start_capture(detection_callback)
        
        return {"message": "Live detection started", "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start live detection: {str(e)}")


@router.post("/stop-live-detection")
async def stop_live_detection():
    """Stop live detection"""
    try:
        camera = get_camera()
        camera.stop_capture()
        return {"message": "Live detection stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop live detection: {str(e)}")


@router.get("/detection-status")
async def get_detection_status():
    """Get current detection status"""
    try:
        camera = get_camera()
        detector = get_detector()
        
        camera_info = camera.get_camera_info()
        model_info = detector.get_model_info()
        
        return {
            "camera": camera_info,
            "model": model_info,
            "status": "running" if camera_info.get('is_running') else "stopped"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")