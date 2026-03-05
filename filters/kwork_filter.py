"""
Фильтр для @kworkMarket_bot
Парсит и фильтрует заказы с Kwork
"""
import re
from typing import Optional, Dict, Any
from datetime import datetime

class KworkFilter:
    """Фильтр заказов с Kwork"""
    
    # Ключевые слова для фильтрации
    KEYWORDS = ["python", "bot", "парсинг", "scraping", "webhook", "api", "django", "fastapi"]
    
    # Минимальная цена (в рублях)
    MIN_PRICE = 1000
    
    def __init__(self):
        self.price_pattern = re.compile(r'([\d]+)\s*-?\s*([\d]*)₽', re.IGNORECASE)
        self.price_min_pattern = re.compile(r'от\s+([\d]+)₽', re.IGNORECASE)
    
    def extract_price(self, text: str) -> Optional[int]:
        """Извлекает минимальную цену из текста"""
        
        # Поиск "от 2000₽"
        match = self.price_min_pattern.search(text)
        if match:
            return int(match.group(1))
        
        # Поиск "2000-5000₽"
        match = self.price_pattern.search(text)
        if match:
            min_price = int(match.group(1))
            return min_price
        
        return None
    
    def is_relevant(self, text: str) -> bool:
        """Проверяет релевантность заказа"""
        
        # Проверка ключевых слов
        text_lower = text.lower()
        has_keyword = any(kw in text_lower for kw in self.KEYWORDS)
        
        if not has_keyword:
            return False
        
        # Проверка цены
        price = self.extract_price(text)
        if price and price < self.MIN_PRICE:
            return False
        
        return True
    
    def extract_info(self, text: str) -> Dict[str, Any]:
        """Извлекает информацию из сообщения"""
        
        info = {
            "title": self._extract_title(text),
            "price": self.extract_price(text),
            "urgency": self._extract_urgency(text),
            "timestamp": datetime.now()
        }
        
        return info
    
    def _extract_title(self, text: str) -> str:
        """Извлекает заголовок заказа"""
        # Первая строка обычно заголовок
        lines = text.strip().split('\n')
        if lines:
            title = lines[0].strip().replace("🔥 Заказ:", "").strip()
            return title
        return text[:50]
    
    def _extract_urgency(self, text: str) -> bool:
        """Проверяет срочность"""
        urgency_keywords = ["срочно", "сегодня", "urgent", "fast"]
        text_lower = text.lower()
        return any(kw in text_lower for kw in urgency_keywords)


# Глобальный экземпляр
kwork_filter = KworkFilter()
