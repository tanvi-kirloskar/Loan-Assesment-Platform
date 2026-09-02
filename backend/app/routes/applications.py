from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import LoanApplicationCreate, LoanApplicationResponse
from app.services.assessment import assess_loan
from app.auth import get_current_user
from app.models import Applicant, LoanApplication, User

router = APIRouter()


@router.post(
    "/applications",
    response_model=LoanApplicationResponse,
)
def create_application(
    application: LoanApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = assess_loan(
        monthly_income=application.monthly_income,
        loan_amount=application.loan_amount,
    )

    new_applicant = Applicant(
        full_name=application.full_name,
        monthly_income=application.monthly_income,
        age=None,
        employment_type=None,
        employer=None,
        years_employed=None,
        user_id=current_user.id,
    )

    db.add(new_applicant)
    db.flush()

    new_application = LoanApplication(
        applicant_id=new_applicant.id,
        loan_amount=application.loan_amount,
        loan_tenure_months=application.loan_tenure_months,
        loan_purpose=application.loan_purpose,
        existing_monthly_emi=application.existing_monthly_emi,
        status="submitted",
        decision=assessment["decision"],
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application


@router.get(
    "/applications/{application_id}",
    response_model=LoanApplicationResponse,
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(LoanApplication)
        .join(Applicant)
        .filter(
            LoanApplication.id == application_id,
            Applicant.user_id == current_user.id,
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application