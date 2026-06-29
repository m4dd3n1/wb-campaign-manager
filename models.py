from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class AnalysisRun(Base):
    """Запись о проведенном анализе"""
    __tablename__ = "analysis_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_campaigns = Column(Integer)
    deleted_clusters_count = Column(Integer, default=0)
    cpo_threshold = Column(Float)  # Порог CPO в процентах
    
    deleted_clusters = relationship("DeletedCluster", back_populates="analysis_run")


class DeletedCluster(Base):
    """Информация об удаленном кластере"""
    __tablename__ = "deleted_clusters"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_run_id = Column(Integer, ForeignKey("analysis_runs.id"))
    campaign_id = Column(String, index=True)
    cluster_id = Column(String, index=True)
    cpo = Column(Float)  # CPO в процентах
    product_price = Column(Float)
    reason = Column(String)  # Причина удаления
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis_run = relationship("AnalysisRun", back_populates="deleted_clusters")


class Campaign(Base):
    """Информация о кампании"""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String, unique=True, index=True)
    name = Column(String)
    status = Column(String, default="active")
    last_analyzed = Column(DateTime, default=datetime.utcnow)
