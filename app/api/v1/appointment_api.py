from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime

from app.api.v1.auth import get_current_patient, get_current_doctor, get_current_user
from app.api.dependencies import get_db
from app.models.appointment import AppointmentCreate, AppointmentOut, AppointmentStatus
from app.models.roles import Role
from app.schema.users import User as UserModel
from app.schema.appointment import Appointment as AppointmentModel

router = APIRouter()


@router.get("/appointments", response_model=List[AppointmentOut])
def get_my_appointments_as_doctor(
    db: Session = Depends(get_db),
    current_doctor: UserModel = Depends(get_current_doctor),
):
    """
    Get a list of all appointments for the currently logged-in doctor.
    """
    return current_doctor.appointments_as_doctor


@router.post("/book-appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(
    appointment_in: AppointmentCreate,
    db: Session = Depends(get_db),
    current_patient: UserModel = Depends(get_current_patient),
):
    """
    Book an appointment with a doctor for the currently logged-in patient.
    """
    doctor = db.query(UserModel).filter(
        UserModel.id == appointment_in.doctor_id,
        UserModel.role == Role.DOCTOR
    ).first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found.")

    # --- Availability Check ---
    appointment_day = appointment_in.appointment_time.strftime("%A").lower()  # e.g., "monday"
    appointment_time = appointment_in.appointment_time.time()

    is_available = False
    for slot in doctor.availabilities:
        if slot.day_of_week.value == appointment_day:
            if slot.start_time <= appointment_time < slot.end_time:
                is_available = True
                break

    if not is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The requested time slot is outside the doctor's availability."
        )

    # --- Conflict Check ---
    existing_appointment = db.query(AppointmentModel).filter(
        AppointmentModel.doctor_id == appointment_in.doctor_id,
        AppointmentModel.appointment_time == appointment_in.appointment_time,
        AppointmentModel.status != AppointmentStatus.CANCELLED
    ).first()

    if existing_appointment:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This time slot is already booked.")

    # --- Create Appointment ---
    new_appointment = AppointmentModel(
        **appointment_in.model_dump(),
        patient_id=current_patient.id
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return new_appointment


@router.patch("/appointments/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Cancel an appointment.
    Can be cancelled by either the patient who booked it or the doctor it's with.
    """
    # Fetch the appointment from the DB
    appointment = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()

    # Check if appointment exists
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

    # Authorization check: only the patient or the doctor can cancel
    if not (current_user.id == appointment.patient_id or current_user.id == appointment.doctor_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to cancel this appointment.")

    # Check if the appointment can be cancelled
    if appointment.status != AppointmentStatus.SCHEDULED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel an appointment with status '{appointment.status.value}'.",
        )

    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    db.refresh(appointment)
    return appointment