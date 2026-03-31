from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["DatasetItem"]] = relationship(
        "DatasetItem", back_populates="dataset", cascade="all, delete-orphan"
    )


class DatasetItem(Base):
    __tablename__ = "dataset_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    item_key: Mapped[str] = mapped_column(String(120), nullable=False)
    input_text: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_keywords: Mapped[list] = mapped_column(JSON, default=list)
    difficulty: Mapped[str] = mapped_column(String(50), default="medium")
    split: Mapped[str] = mapped_column(String(50), default="test")

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="items")


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    workflow_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), default="mock")
    model_name: Mapped[str] = mapped_column(String(100), default="demo-model")
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output_schema_version: Mapped[str] = mapped_column(String(50), default="v1")
    temperature: Mapped[float] = mapped_column(Float, default=0.2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    runs: Mapped[list["EvaluationRun"]] = relationship("EvaluationRun", back_populates="prompt_version")


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_version_id: Mapped[int] = mapped_column(ForeignKey("prompt_versions.id"), nullable=False)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued")
    aggregate_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    run_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    prompt_version: Mapped["PromptVersion"] = relationship("PromptVersion", back_populates="runs")
    item_results: Mapped[list["ItemEvaluationResult"]] = relationship(
        "ItemEvaluationResult", back_populates="run", cascade="all, delete-orphan"
    )


class ItemEvaluationResult(Base):
    __tablename__ = "item_evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("evaluation_runs.id"), nullable=False, index=True)
    dataset_item_id: Mapped[int] = mapped_column(ForeignKey("dataset_items.id"), nullable=False)
    raw_output: Mapped[dict] = mapped_column(JSON, nullable=False)
    structured_output: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    rubric_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    metric_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    evaluator_notes: Mapped[list] = mapped_column(JSON, default=list)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)

    run: Mapped["EvaluationRun"] = relationship("EvaluationRun", back_populates="item_results")
