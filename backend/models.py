"""Modelos: Lead (formulario), Config (singleton del sitio) y Project (CMS)."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="new", server_default="new")
    contacted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Config(Base):
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str] = mapped_column(String(100), default="Julian Cano", server_default="Julian Cano")
    role_title: Mapped[str] = mapped_column(
        String(200),
        default="Full Stack & AI Developer | AWS Cloud | AI Automation & Agents",
        server_default="Full Stack & AI Developer | AWS Cloud | AI Automation & Agents",
    )
    tagline: Mapped[str] = mapped_column(
        Text,
        default="",
        server_default="",
    )
    accent_color: Mapped[str] = mapped_column(String(7), default="#6d28d9", server_default="#6d28d9")
    secondary_color: Mapped[str] = mapped_column(
        String(7), default="#0d9488", server_default="#0d9488"
    )
    linkedin_url: Mapped[str] = mapped_column(
        String(255), default="https://www.linkedin.com/in/juliancanodev/", server_default="https://www.linkedin.com/in/juliancanodev/"
    )
    github_url: Mapped[str] = mapped_column(
        String(255), default="https://github.com/JulianCanoDev", server_default="https://github.com/JulianCanoDev"
    )
    whatsapp_phone: Mapped[str] = mapped_column(
        String(50), default="573237073472", server_default="573237073472"
    )
    cv_url: Mapped[str] = mapped_column(
        String(500), default="/CV_Julian_Cano.pdf", server_default="/CV_Julian_Cano.pdf"
    )
    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        default=list,
        server_default="{}",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    title_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category: Mapped[str] = mapped_column(String(100), default="Web", server_default="Web")
    category_en: Mapped[str | None] = mapped_column(String(100), nullable=True)
    challenge: Mapped[str | None] = mapped_column(Text, nullable=True)
    challenge_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    solution_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, server_default="{}"
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
