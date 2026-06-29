from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class CampaignAnalysisRequest(BaseModel):
    """Запрос на анализ кампаний"""
    api_key: str
    campaign_ids: List[str]
    cpo_threshold: float = 10.0  # Порог CPO в процентах (по умолчанию 10%)


class DeletedClusterResponse(BaseModel):
    """Информация об удаленном кластере"""
    id: int
    campaign_id: str
    cluster_id: str
    cpo: float
    product_price: float
    reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisRunResponse(BaseModel):
    """Информация о проведенном анализе"""
    id: int
    created_at: datetime
    total_campaigns: int
    deleted_clusters_count: int
    cpo_threshold: float
    deleted_clusters: List[DeletedClusterResponse] = []
    
    class Config:
        from_attributes = True
