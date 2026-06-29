from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os
from pathlib import Path

from models import Base, Campaign, DeletedCluster, AnalysisRun
from schemas import CampaignAnalysisRequest, DeletedClusterResponse, AnalysisRunResponse
from database import get_db
from wb_api import WildberriesAPI
from analysis import analyze_campaigns

# Создаем базовую директорию
BASE_DIR = Path(__file__).resolve().parent

# Инициализируем БД
DATABASE_URL = "sqlite:///./wb_campaigns.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Инициализируем FastAPI
app = FastAPI(title="Wildberries Campaign Manager", version="1.0.0")

# Монтируем статические файлы
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    """Возвращает главную страницу"""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/analyze")
async def analyze(request: CampaignAnalysisRequest, db: Session = Depends(get_db)):
    """
    Анализирует кампании и удаляет кластеры с высоким CPO
    
    Parameters:
    - api_key: API ключ Wildberries
    - campaign_ids: Список ID кампаний для анализа
    - cpo_threshold: Максимальный CPO в процентах от цены товара (по умолчанию 10)
    """
    try:
        # Инициализируем API Wildberries
        wb_api = WildberriesAPI(api_key=request.api_key)
        
        # Создаем запись анализа
        analysis_run = AnalysisRun(
            total_campaigns=len(request.campaign_ids),
            cpo_threshold=request.cpo_threshold
        )
        db.add(analysis_run)
        db.commit()
        
        # Анализируем кампании
        deleted_clusters = []
        for campaign_id in request.campaign_ids:
            try:
                campaign_data = wb_api.get_campaign_data(campaign_id)
                results = analyze_campaigns(
                    campaign_data,
                    campaign_id,
                    request.cpo_threshold
                )
                
                # Удаляем неподходящие кластеры через API
                for result in results:
                    if result["should_delete"]:
                        wb_api.delete_cluster(campaign_id, result["cluster_id"])
                        
                        # Сохраняем информацию об удаленном кластере в БД
                        deleted_cluster = DeletedCluster(
                            analysis_run_id=analysis_run.id,
                            campaign_id=campaign_id,
                            cluster_id=result["cluster_id"],
                            cpo=result["cpo"],
                            product_price=result["product_price"],
                            reason=result["reason"]
                        )
                        db.add(deleted_cluster)
                        deleted_clusters.append(result)
                
                # Сохраняем кампанию
                campaign = Campaign(
                    campaign_id=campaign_id,
                    name=campaign_data.get("name", f"Campaign {campaign_id}"),
                    status="analyzed"
                )
                db.merge(campaign)
                
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Ошибка обработки кампании {campaign_id}: {str(e)}")
        
        db.commit()
        analysis_run.deleted_clusters_count = len(deleted_clusters)
        db.commit()
        
        return {
            "success": True,
            "message": f"Анализ завершен. Удалено кластеров: {len(deleted_clusters)}",
            "deleted_clusters": deleted_clusters,
            "analysis_run_id": analysis_run.id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")


@app.get("/api/analysis-history")
async def get_analysis_history(db: Session = Depends(get_db)):
    """Возвращает историю анализов"""
    runs = db.query(AnalysisRun).order_by(AnalysisRun.created_at.desc()).limit(50).all()
    return runs


@app.get("/api/analysis/{analysis_id}/clusters")
async def get_deleted_clusters(analysis_id: int, db: Session = Depends(get_db)):
    """Возвращает удаленные кластеры для конкретного анализа"""
    clusters = db.query(DeletedCluster).filter(
        DeletedCluster.analysis_run_id == analysis_id
    ).all()
    return clusters


@app.get("/api/campaigns")
async def get_campaigns(db: Session = Depends(get_db)):
    """Возвращает список всех кампаний"""
    campaigns = db.query(Campaign).all()
    return campaigns


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
