from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationOut])
def lister_notifications(non_lues_seulement: bool = False, db: Session = Depends(get_db)):
    query = db.query(Notification)
    if non_lues_seulement:
        query = query.filter(Notification.lue == False)
    return query.order_by(Notification.date_creation.desc()).limit(50).all()


@router.patch("/{notification_id}/lire", response_model=NotificationOut)
def marquer_lue(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    notif.lue = True
    db.commit()
    db.refresh(notif)
    return notif


@router.patch("/lire-tout")
def marquer_toutes_lues(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.lue == False).update({"lue": True})
    db.commit()
    return {"message": "Toutes les notifications ont été marquées comme lues"}
