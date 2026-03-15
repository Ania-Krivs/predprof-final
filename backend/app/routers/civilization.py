
from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from datetime import timedelta
from pathlib import Path
import tempfile
import json
import numpy as np
from tensorflow import keras

from app.data.models import User
from app.data import schemas
from app.utils.error import Error
from app.utils.auth import create_user, authenticate_user
from app.utils.security import verify_password, get_current_user
from app.ml_engine.parser.online_parser import parse_audio, load_label_mapping

from typing import Annotated
from typing import List
import uuid
from fastapi import status


router = APIRouter(prefix="/civilization", tags=["Civilization"])


def normalize_audio_features(x: np.ndarray) -> np.ndarray:
    """Нормализирует аудиофичи как в training.py"""
    x = np.asarray(x).astype("float32")
    mean = np.mean(x)
    std = np.std(x) + 1e-8
    x = (x - mean) / std
    return x


def get_model_path() -> Path:
    """Получает путь к обученной модели"""
    # Путь относительно корня проекта
    model_path = Path(__file__).parent.parent / "ml_engine" / "artifacts" / "best_model.h5"
    return model_path


@router.post("/")
async def get_civilization(file: UploadFile = File(...)):
    """
    Классифицирует цивилизацию по звуковому файлу mp3.
    
    Args:
        file: MP3 аудиофайл для анализа
        
    Returns:
        JSON с названием классифицированной цивилизации и уверенностью
    """
    try:
        # Проверка расширения файла
        if not file.filename.lower().endswith(('.mp3', '.wav', '.flac')):
            raise HTTPException(
                status_code=400,
                detail="Поддерживаются только mp3, wav, flac файлы"
            )
        
        # Сохранение временного файла
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Парсинг аудио
            audio_features = parse_audio(tmp_path)
            
            # Нормализация
            audio_features = normalize_audio_features(audio_features)
            
            # Добавление batch dimension и channel dimension если нужно
            if audio_features.ndim == 1:
                audio_features = np.expand_dims(audio_features, axis=(0, -1))
            elif audio_features.ndim == 2:
                audio_features = np.expand_dims(audio_features, axis=0)
            
            # Загрузка модели
            model_path = get_model_path()
            if not model_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail=f"Обученная модель не найдена в {model_path}"
                )
            
            model = keras.models.load_model(str(model_path))
            
            # Предсказание
            predictions = model.predict(audio_features, verbose=0)
            pred_class_idx = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][pred_class_idx])
            
            # Загрузка маппинга классов
            mapping = load_label_mapping()
            civilization_name = mapping["class_id_to_label"].get(str(pred_class_idx), "Unknown")
            
            all_predictions = {
                mapping["class_id_to_label"].get(str(i), "Unknown"): float(predictions[0][i])
                for i in range(len(predictions[0]))
            }
            
            return schemas.CivilizationClassificationResponse(
                civilization=civilization_name,
                confidence=round(confidence, 4),
                class_id=pred_class_idx,
                all_predictions=all_predictions
            )
        
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    
    except HTTPException:
        raise
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Отсутствует необходимая библиотека: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при классификации: {str(e)}"
        )

