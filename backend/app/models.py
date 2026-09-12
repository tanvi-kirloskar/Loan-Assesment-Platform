from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
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

    documents: Mapped[list["Document"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
    )

    verification_findings: Mapped[list["VerificationFinding"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
    )


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("loan_applications.id"),
        nullable=False,
    )

    document_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="UPLOADED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    application: Mapped["LoanApplication"] = relationship(
        back_populates="documents",
    )

    evidence: Mapped[list["DocumentEvidence"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentEvidence(Base):
    __tablename__ = "document_evidence"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
    )

    field_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    extracted_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    document: Mapped["Document"] = relationship(
        back_populates="evidence",
    )


class VerificationFinding(Base):
    __tablename__ = "verification_findings"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    application_id: Mapped[int] = mapped_column(
        ForeignKey("loan_applications.id"),
        nullable=False,
    )

    finding_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    application: Mapped["LoanApplication"] = relationship(
        back_populates="verification_findings",
    )