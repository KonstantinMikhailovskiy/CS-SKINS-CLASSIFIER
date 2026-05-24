# model_api.py - API сервер для Random Forest модели
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
import pickle
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CS:GO Skin Price Predictor API")

# Разрешаем CORS для Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальные переменные для загруженных моделей
model = None
imputer = None
columns = None
df_skins = None


class SkinPredictionRequest(BaseModel):
    """Модель запроса для предсказания"""
    Weapon: str
    Case: str
    Rarity: str = "Unknown"
    Case_1: str = "Unknown"
    Min_Wear: float = 0.0
    Max_Wear: float = 0.75
    # Цены разных качеств (опционально)
    Factory_New: Optional[float] = None
    Minimal_Wear: Optional[float] = None
    Field_Tested: Optional[float] = None
    Well_Worn: Optional[float] = None
    Battle_Scarred: Optional[float] = None
    # StatTrak цены (опционально)
    StatTrak_Factory_New: Optional[float] = None
    StatTrak_Minimal_Wear: Optional[float] = None
    StatTrak_Field_Tested: Optional[float] = None
    StatTrak_Well_Worn: Optional[float] = None
    StatTrak_Battle_Scarred: Optional[float] = None


class PredictionResponse(BaseModel):
    """Модель ответа"""
    predicted_price: float
    confidence: Optional[float] = None
    weapon: str
    skin: str
    rarity: str
    status: str
    real_price: Optional[float] = None


class SkinInfoResponse(BaseModel):
    """Информация о скине"""
    weapon: str
    skin: str
    rarity: str
    case: str
    min_wear: float
    max_wear: float
    factory_new_price: Optional[float]
    prices: Dict[str, float]
    stattrak_prices: Dict[str, float]


@app.on_event("startup")
async def load_models():
    """Загрузка моделей при старте сервера"""
    global model, imputer, columns, df_skins

    try:
        # Загрузка Random Forest модели
        with open('cs_model_rf.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✅ Random Forest модель загружена")

        # Загрузка imputer
        with open('cs_imputer_rf.pkl', 'rb') as f:
            imputer = pickle.load(f)
        print("✅ Imputer загружен")

        # Загрузка колонок
        with open('cs_columns_rf.pkl', 'rb') as f:
            columns = pickle.load(f)
        print(f"✅ Загружено {len(columns)} признаков")

        # Загрузка базы данных скинов
        df_skins = pd.read_csv('Cs_skins.csv')

        # Очистка данных
        price_columns = ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred',
                         'StatTrak Factory New', 'StatTrak Minimal Wear', 'StatTrak Field-Tested',
                         'StatTrak Well-Worn', 'StatTrak Battle-Scarred']

        for col in price_columns:
            if col in df_skins.columns:
                df_skins[col] = df_skins[col].astype(str)
                df_skins[col] = df_skins[col].str.replace('$', '', regex=False)
                df_skins[col] = df_skins[col].str.replace(',', '', regex=False)
                df_skins[col] = df_skins[col].replace('Not Possible', np.nan)
                df_skins[col] = df_skins[col].replace('No Recent Price', np.nan)
                df_skins[col] = pd.to_numeric(df_skins[col], errors='coerce')

        print(f"✅ Загружено {len(df_skins)} скинов из базы данных")

    except Exception as e:
        print(f"❌ Ошибка загрузки моделей: {str(e)}")


@app.get("/")
async def root():
    """Проверка работоспособности API"""
    return {
        "status": "online",
        "message": "CS:GO Skin Price Predictor API (Random Forest)",
        "model_loaded": model is not None,
        "model_type": "Random Forest Regressor"
    }


@app.get("/weapons")
async def get_weapons() -> Dict[str, List[str]]:
    """Получить список всех оружий"""
    if df_skins is None:
        raise HTTPException(status_code=500, detail="База данных не загружена")

    weapons = sorted(df_skins['Weapon'].unique().tolist())
    return {"weapons": weapons}


@app.get("/skins/{weapon}")
async def get_skins(weapon: str) -> Dict[str, List[str]]:
    """Получить список скинов для оружия"""
    if df_skins is None:
        raise HTTPException(status_code=500, detail="База данных не загружена")

    skins = df_skins[df_skins['Weapon'] == weapon]['Case'].unique().tolist()
    return {"skins": sorted(skins)}


@app.post("/predict", response_model=PredictionResponse)
async def predict_price(request: SkinPredictionRequest):
    """Предсказание цены скина с помощью Random Forest"""
    global model, imputer, columns

    if model is None:
        raise HTTPException(status_code=500, detail="Модель не загружена")

    try:
        # Создаем словарь с данными
        data = {
            'Weapon': request.Weapon,
            'Case': request.Case,
            'Rarity': request.Rarity if request.Rarity != "Unknown" else "Mil-Spec",
            'Case_1': request.Case_1 if request.Case_1 != "Unknown" else "Unknown Case",
            'Min Wear': request.Min_Wear,
            'Max Wear': request.Max_Wear,
        }

        # Добавляем цены других качеств
        if request.Minimal_Wear is not None:
            data['Minimal Wear'] = request.Minimal_Wear
        if request.Field_Tested is not None:
            data['Field-Tested'] = request.Field_Tested
        if request.Well_Worn is not None:
            data['Well-Worn'] = request.Well_Worn
        if request.Battle_Scarred is not None:
            data['Battle-Scarred'] = request.Battle_Scarred

        # Добавляем StatTrak цены
        data['StatTrak Factory New'] = request.StatTrak_Factory_New if request.StatTrak_Factory_New is not None else 0
        data[
            'StatTrak Minimal Wear'] = request.StatTrak_Minimal_Wear if request.StatTrak_Minimal_Wear is not None else 0
        data[
            'StatTrak Field-Tested'] = request.StatTrak_Field_Tested if request.StatTrak_Field_Tested is not None else 0
        data['StatTrak Well-Worn'] = request.StatTrak_Well_Worn if request.StatTrak_Well_Worn is not None else 0
        data[
            'StatTrak Battle-Scarred'] = request.StatTrak_Battle_Scarred if request.StatTrak_Battle_Scarred is not None else 0

        # Создаем дополнительные признаки
        if request.Minimal_Wear is not None and request.Minimal_Wear > 0:
            data['Ratio_FN_MW'] = 1 / (request.Minimal_Wear + 0.01)
        else:
            data['Ratio_FN_MW'] = 0

        if request.Field_Tested is not None and request.Field_Tested > 0:
            data['Ratio_FN_FT'] = 1 / (request.Field_Tested + 0.01)
        else:
            data['Ratio_FN_FT'] = 0

        if request.Battle_Scarred is not None and request.Battle_Scarred > 0:
            data['Price_Spread'] = 100 - request.Battle_Scarred
        else:
            data['Price_Spread'] = 0

        data['Wear_Range'] = request.Max_Wear - request.Min_Wear

        # Создаем DataFrame
        df_in = pd.DataFrame([data])

        # One-hot encoding
        categorical_cols = ['Weapon', 'Case', 'Rarity', 'Case_1']
        existing_cats = [c for c in categorical_cols if c in df_in.columns]
        df_in = pd.get_dummies(df_in, columns=existing_cats, drop_first=True)

        # Выравниваем колонки
        df_in = df_in.reindex(columns=columns, fill_value=0)

        # Применяем imputer
        df_in = pd.DataFrame(imputer.transform(df_in), columns=columns)

        # Предсказание
        predicted_price = float(model.predict(df_in)[0])
        predicted_price = max(0, predicted_price)  # Цена не может быть отрицательной

        # Получаем реальную цену из БД если есть
        real_price = None
        confidence = None
        status = "predicted"

        if df_skins is not None:
            mask = (df_skins['Weapon'] == request.Weapon) & (df_skins['Case'] == request.Case)
            real_skin = df_skins[mask]
            if len(real_skin) > 0 and pd.notna(real_skin['Factory New'].iloc[0]):
                real_price = float(real_skin['Factory New'].iloc[0])
                # Рассчитываем точность предсказания
                error_percent = abs(predicted_price - real_price) / real_price * 100
                confidence = max(0, 100 - error_percent)
                if error_percent < 20:
                    status = "accurate"
                elif error_percent < 50:
                    status = "approximate"
                else:
                    status = "low_confidence"

        return PredictionResponse(
            predicted_price=predicted_price,
            confidence=confidence,
            weapon=request.Weapon,
            skin=request.Case,
            rarity=request.Rarity,
            status=status,
            real_price=real_price
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка предсказания: {str(e)}")


@app.get("/skin-info/{weapon}/{skin_name}", response_model=SkinInfoResponse)
async def get_skin_info(weapon: str, skin_name: str):
    """Получить полную информацию о скине из базы"""
    if df_skins is None:
        raise HTTPException(status_code=500, detail="База данных не загружена")

    mask = (df_skins['Weapon'] == weapon) & (df_skins['Case'] == skin_name)
    skin_data = df_skins[mask]

    if len(skin_data) == 0:
        raise HTTPException(status_code=404, detail="Скин не найден")

    row = skin_data.iloc[0]

    # Собираем цены
    prices = {}
    for condition in ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred']:
        if condition in row and pd.notna(row[condition]):
            prices[condition] = float(row[condition])

    stattrak_prices = {}
    for st_condition in ['StatTrak Factory New', 'StatTrak Minimal Wear', 'StatTrak Field-Tested',
                         'StatTrak Well-Worn', 'StatTrak Battle-Scarred']:
        if st_condition in row and pd.notna(row[st_condition]):
            stattrak_prices[st_condition.replace('StatTrak ', '')] = float(row[st_condition])

    return SkinInfoResponse(
        weapon=weapon,
        skin=skin_name,
        rarity=row.get('Rarity', 'Unknown'),
        case=row.get('Case_1', 'Unknown'),
        min_wear=float(row.get('Min Wear', 0)) if pd.notna(row.get('Min Wear')) else 0,
        max_wear=float(row.get('Max Wear', 1)) if pd.notna(row.get('Max Wear')) else 1,
        factory_new_price=float(row['Factory New']) if pd.notna(row['Factory New']) else None,
        prices=prices,
        stattrak_prices=stattrak_prices
    )


@app.post("/train")
async def retrain_model():
    """Переобучить модель (для администрирования)"""
    # Здесь можно добавить логику переобучения
    return {"message": "Retraining endpoint - implement as needed"}


if __name__ == "__main__":
    print("🚀 Запуск CS:GO Skin Price Predictor API...")
    print("📍 API будет доступен по адресу: http://localhost:8200")
    print("📖 Документация: http://localhost:8200/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8200)