from fastapi import APIRouter, UploadFile
import io
import librosa
import numpy as np
router = APIRouter(prefix="/ml", tags=["ML Work"])


@router.post("/request")
async def request_to_ml(data: UploadFile):
    file = await data.read()
    audio_file = io.BytesIO(file)
    y, sr = librosa.load(audio_file, sr=22050)
    mfccs = librosa.feature.mfccs(y=y, sr=sr, n_mfcc=13)
    mfccs_scaled = np.mean(mfccs.T, axis=0 )
    tensor = np.array([mfccs_scaled], dtype="float32")
    # model.predict(tensor)

