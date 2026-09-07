from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="APPLICANT",
    )

    applicant: Mapped["Applicant | None"] = relationship(
        back_populates="user",
        uselist=False,
    )


class Applicant(Base):
    __tablename__ = "applicants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    employment_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    employer: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    years_employed: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    monthly_income: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    user: Mapped["User | None"] = relationship(
        back_populates="applicant",
    )

    loan_applications: Mapped[list["LoanApplication"]] = relationship(
        back_populates="applicant",
    )


class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    applicant_id: Mapped[int] = mapped_column(
        ForeignKey("applicants.id"),
        nullable=False,
    )

    loan_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    loan_tenure_months: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    loan_purpose: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    existing_monthly_emi: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="submitted",
    )

    decision: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    credit_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    credit_score_source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    interest_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    emi: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    foir: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    lti: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        nullable=True,
    )

    assessment_reasons: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    applicant: Mapped["Applicant"] = relationship(
        back_populates="loan_applications",
    )