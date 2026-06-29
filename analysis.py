from typing import List, Dict, Any


def analyze_campaigns(
    campaign_data: Dict[str, Any],
    campaign_id: str,
    cpo_threshold: float
) -> List[Dict[str, Any]]:
    """
    Анализирует кластеры кампании и определяет, какие нужно удалить
    
    Args:
        campaign_data: Данные кампании с кластерами
        campaign_id: ID кампании
        cpo_threshold: Максимальный CPO в процентах от цены товара
        
    Returns:
        Список результатов анализа с информацией о кластерах для удаления
    """
    results = []
    
    clusters = campaign_data.get("clusters", [])
    
    for cluster in clusters:
        cluster_id = cluster.get("id")
        cpo_percentage = cluster.get("cpo", 0)
        product_price = cluster.get("price", 0)
        cpo_absolute = cluster.get("cpo_absolute", 0)
        
        # Определяем, нужно ли удалить кластер
        should_delete = cpo_percentage > cpo_threshold
        
        result = {
            "cluster_id": cluster_id,
            "cpo": cpo_percentage,  # CPO в процентах
            "product_price": product_price,
            "should_delete": should_delete,
            "reason": f"CPO {cpo_percentage:.2f}% превышает лимит {cpo_threshold}%" if should_delete else "OK"
        }
        
        results.append(result)
    
    return results
