"""
Универсальный фильтр для всех заказов
Собирает всё, без фильтрации по ключевым словам
"""
from typing import Dict, Any
from datetime import datetime

class UniversalFilter:
    """Фильтр для сбора всех заказов"""
    
    # Минимальная цена для сбора (можно 0 = всё)
    MIN_PRICE = 0
    
    def __init__(self):
        self.price_pattern = None
    
    def extract_price(self, text: str) -> int:
        """Извлекает минимальную цену из текста"""
        import re
        
        # Поиск "от 2000₽"
        match = re.search(r'от\s+([\d]+)₽', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        # Поиск "2000-5000₽"
        match = re.search(r'([\d]+)\s*-\s*([\d]+)₽', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        
        return 0
    
    def is_relevant(self, text: str) -> bool:
        """Принимает ВСЁ (фильтр отключён)"""
        return True
    
    def extract_info(self, text: str) -> Dict[str, Any]:
        """Извлекает информацию из сообщения"""
        import re
        
        # Извлекаем заголовок (первая строка без эмодзи)
        lines = text.strip().split('\n')
        title = ""
        if lines:
            title = re.sub(r'[🔥💰⏰📝🔗]', '', lines[0]).strip()
        
        # Извлекаем цену
        price = self.extract_price(text)
        
        # Проверяем срочность
        urgency_keywords = ["срочно", "сегодня", "urgent", "fast", "🔥"]
        urgency = any(kw in text.lower() for kw in urgency_keywords)
        
        info = {
            "title": title[:100],
            "price": price,
            "urgency": urgency,
            "timestamp": datetime.now(),
            "full_text": text[:2000]  # Полный текст для дальнейшего анализа
        }
        
        return info


# Глобальный экземпляр (без фильтрации)
universal_filter = UniversalFilter()
