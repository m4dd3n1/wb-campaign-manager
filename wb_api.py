import requests
from typing import Dict, List, Any
from datetime import datetime, timedelta


class WildberriesAPI:
    """Класс для работы с API Wildberries"""
    
    # Примеры base URL (нужно уточнить у документации WB)
    BASE_URL = "https://api-seller.wildberries.ru"
    
    def __init__(self, api_key: str):
        """
        Инициализация API клиента
        
        Args:
            api_key: API ключ Wildberries
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def get_campaign_data(self, campaign_id: str) -> Dict[str, Any]:
        """
        Получает данные о кампании и её кластерах
        
        Пример структуры ответа:
        {
            "name": "Campaign Name",
            "clusters": [
                {
                    "id": "cluster_123",
                    "name": "Cluster Name",
                    "product_id": "product_123",
                    "price": 1000,
                    "spent": 500,
                    "orders": 10,
                    "cpc": 50,
                    "conversions": 2
                }
            ]
        }
        """
        try:
            # Пример endpoint - нужно уточнить реальный URL у документации WB
            url = f"{self.BASE_URL}/v1/campaigns/{campaign_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Обогащаем данные кластеров
            if "clusters" in data:
                for cluster in data["clusters"]:
                    # Вычисляем CPO (Cost Per Order)
                    orders = cluster.get("orders", 0)
                    spent = cluster.get("spent", 0)
                    
                    if orders > 0:
                        cpo = (spent / orders)
                    else:
                        cpo = spent if spent > 0 else 0
                    
                    # Вычисляем CPO в процентах от цены товара
                    price = cluster.get("price", 1)
                    cluster["cpo"] = (cpo / price * 100) if price > 0 else 0
                    cluster["cpo_absolute"] = cpo
            
            return data
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при получении данных кампании: {str(e)}")
    
    def delete_cluster(self, campaign_id: str, cluster_id: str) -> bool:
        """
        Удаляет кластер из кампании
        
        Args:
            campaign_id: ID кампании
            cluster_id: ID кластера
            
        Returns:
            True если успешно, иначе False
        """
        try:
            # Пример endpoint - нужно уточнить реальный URL у документации WB
            url = f"{self.BASE_URL}/v1/campaigns/{campaign_id}/clusters/{cluster_id}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return True
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при удалении кластера: {str(e)}")
    
    def pause_cluster(self, campaign_id: str, cluster_id: str) -> bool:
        """
        Паузирует кластер (альтернатива удалению)
        
        Args:
            campaign_id: ID кампании
            cluster_id: ID кластера
            
        Returns:
            True если успешно, иначе False
        """
        try:
            # Пример endpoint - нужно уточнить реальный URL у документации WB
            url = f"{self.BASE_URL}/v1/campaigns/{campaign_id}/clusters/{cluster_id}/pause"
            response = requests.post(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return True
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при паузировании кластера: {str(e)}")
