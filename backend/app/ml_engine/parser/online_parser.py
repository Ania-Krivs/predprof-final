import numpy as np
from pathlib import Path
import json


def parse_audio(file_path: str) -> np.ndarray:
    """
    Парсит аудиофайл mp3 и возвращает обработанный numpy массив.
    
    Args:
        file_path: Путь к mp3 файлу
        
    Returns:
        numpy.ndarray: Обработанный звуковой сигнал
    """
    try:
        import librosa
    except ImportError:
        raise ImportError("librosa не установлена. Установите: pip install librosa")
    
    y, sr = librosa.load(file_path, sr=22050)
    
    # Приведение к фиксированной длине (2 секунды)
    target_length = sr * 2
    if len(y) < target_length:
        y = np.pad(y, (0, target_length - len(y)), mode='constant')
    else:
        y = y[:target_length]
    
    # Нормализация
    y = (y - np.mean(y)) / (np.std(y) + 1e-8)
    
    return y.astype(np.float32)


def load_label_mapping(mapping_path: str = None) -> dict:
    """
    Загружает отображение класс ID на названия.
    """
    if mapping_path is None:
        mapping_path = Path(__file__).parent.parent / "data" / "label_mapping.json"
    
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    
    return mapping
