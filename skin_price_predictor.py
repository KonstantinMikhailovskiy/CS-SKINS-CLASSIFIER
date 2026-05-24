import streamlit as st
import pandas as pd
import numpy as np
import requests
from difflib import get_close_matches
from datetime import datetime

# URL API (можно настроить через переменные окружения)
API_URL = "http://localhost:8200"


class SkinPricePredictor:
    def __init__(self):
        """Инициализация предсказателя с подключением к API"""
        self.df_skins = None
        self.is_loaded = False
        self.api_available = False

    def check_api(self):
        """Проверка доступности API"""
        try:
            response = requests.get(f"{API_URL}/", timeout=2)
            if response.status_code == 200:
                self.api_available = True
                return True
        except:
            self.api_available = False
        return False

    def load_models(self):
        """Загрузка базы данных скинов (локально для поиска)"""
        try:
            # Проверяем API
            self.check_api()

            # Загружаем CSV локально для быстрого поиска
            self.df_skins = pd.read_csv('Cs_skins.csv')

            # Очистка данных
            price_columns = ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred',
                             'StatTrak Factory New', 'StatTrak Minimal Wear', 'StatTrak Field-Tested',
                             'StatTrak Well-Worn', 'StatTrak Battle-Scarred']

            for col in price_columns:
                if col in self.df_skins.columns:
                    self.df_skins[col] = self.df_skins[col].astype(str)
                    self.df_skins[col] = self.df_skins[col].str.replace('$', '', regex=False)
                    self.df_skins[col] = self.df_skins[col].str.replace(',', '', regex=False)
                    self.df_skins[col] = self.df_skins[col].replace('Not Possible', np.nan)
                    self.df_skins[col] = self.df_skins[col].replace('No Recent Price', np.nan)
                    self.df_skins[col] = pd.to_numeric(self.df_skins[col], errors='coerce')

            self.df_skins = self.df_skins.dropna(subset=['Factory New']).reset_index(drop=True)
            self.is_loaded = True

            api_status = "✅ API доступна" if self.api_available else "⚠️ API не доступна (используется локальный режим)"
            st.success(f"✅ Загружено {len(self.df_skins)} скинов. {api_status}")
            return True

        except Exception as e:
            st.error(f"Ошибка загрузки: {str(e)}")
            return False

    def get_all_weapons(self):
        """Получить список всех оружий"""
        if self.df_skins is not None:
            return sorted(self.df_skins['Weapon'].unique())
        return []

    def get_skins_by_weapon(self, weapon):
        """Получить список скинов для конкретного оружия"""
        if self.df_skins is not None:
            skins = self.df_skins[self.df_skins['Weapon'] == weapon]['Case'].unique()
            return sorted(skins)
        return []

    def get_skin_info(self, weapon, skin_name):
        """Получить полную информацию о скине (через API если доступно)"""
        if self.api_available:
            try:
                response = requests.get(f"{API_URL}/skin-info/{weapon}/{skin_name}", timeout=5)
                if response.status_code == 200:
                    return response.json()
            except:
                pass

        # Fallback на локальный поиск
        if self.df_skins is None:
            return None

        try:
            mask = (self.df_skins['Weapon'] == weapon) & (self.df_skins['Case'] == skin_name)
            skin_data = self.df_skins[mask]

            if len(skin_data) == 0:
                mask = (self.df_skins['Weapon'] == weapon) & (
                    self.df_skins['Case'].str.contains(skin_name, case=False, na=False))
                skin_data = self.df_skins[mask]

            if len(skin_data) > 0:
                row = skin_data.iloc[0]

                price_info = {}
                for condition in ['Factory New', 'Minimal Wear', 'Field-Tested', 'Well-Worn', 'Battle-Scarred']:
                    if condition in row and pd.notna(row[condition]):
                        price_info[condition] = float(row[condition])

                stattrak_info = {}
                for st_condition in ['StatTrak Factory New', 'StatTrak Minimal Wear', 'StatTrak Field-Tested',
                                     'StatTrak Well-Worn', 'StatTrak Battle-Scarred']:
                    if st_condition in row and pd.notna(row[st_condition]):
                        stattrak_info[st_condition.replace('StatTrak ', '')] = float(row[st_condition])

                return {
                    'weapon': weapon,
                    'skin': skin_name,
                    'rarity': row.get('Rarity', 'Unknown'),
                    'case': row.get('Case_1', 'Unknown'),
                    'min_wear': float(row.get('Min Wear', 0)) if pd.notna(row.get('Min Wear')) else 0,
                    'max_wear': float(row.get('Max Wear', 1)) if pd.notna(row.get('Max Wear')) else 1,
                    'prices': price_info,
                    'stattrak_prices': stattrak_info,
                    'factory_new_price': float(row['Factory New']) if pd.notna(row['Factory New']) else None
                }
            return None
        except Exception as e:
            st.error(f"Ошибка поиска скина: {str(e)}")
            return None

    def predict_from_text_input(self, weapon, skin_name, condition='Factory New', stattrak=False):
        """
        Предсказание цены с помощью нейросети (через API)
        """
        if not self.is_loaded:
            if not self.load_models():
                return None

        # Получаем информацию о скине
        skin_info = self.get_skin_info(weapon, skin_name)

        if skin_info:
            # Пробуем использовать нейросеть через API
            if self.api_available:
                try:
                    # Подготавливаем запрос для нейросети
                    request_data = {
                        "Weapon": weapon,
                        "Case": skin_name,
                        "Rarity": skin_info['rarity'],
                        "Case_1": skin_info.get('case', 'Unknown'),
                        "Min_Wear": skin_info.get('min_wear', 0),
                        "Max_Wear": skin_info.get('max_wear', 1)
                    }

                    # Добавляем цены для более точного предсказания
                    for price_cond, price in skin_info.get('prices', {}).items():
                        request_data[price_cond.replace(' ', '_')] = price

                    for st_cond, price in skin_info.get('stattrak_prices', {}).items():
                        request_data[f"StatTrak_{st_cond.replace(' ', '_')}"] = price

                    response = requests.post(f"{API_URL}/predict", json=request_data, timeout=10)

                    if response.status_code == 200:
                        result = response.json()

                        # Корректируем цену для StatTrak
                        predicted_price = result['predicted_price']
                        if stattrak:
                            # StatTrak обычно на 30-50% дороже
                            if skin_info.get('stattrak_prices') and condition in skin_info['stattrak_prices']:
                                predicted_price = skin_info['stattrak_prices'][condition]
                            else:
                                predicted_price = predicted_price * 1.4

                        # Получаем реальную цену если есть
                        actual_price = None
                        if stattrak:
                            if skin_info['stattrak_prices'] and condition in skin_info['stattrak_prices']:
                                actual_price = skin_info['stattrak_prices'][condition]
                        else:
                            if condition in skin_info['prices']:
                                actual_price = skin_info['prices'][condition]

                        return {
                            'predicted_price': predicted_price,
                            'actual_price': actual_price,
                            'weapon': weapon,
                            'skin': skin_name,
                            'rarity': skin_info['rarity'],
                            'condition': condition,
                            'stattrak': stattrak,
                            'min_wear': skin_info['min_wear'],
                            'max_wear': skin_info['max_wear'],
                            'confidence': result.get('confidence'),
                            'source': 'neural_network' if result.get('status') == 'accurate' else 'estimated'
                        }
                except Exception as e:
                    st.warning(f"Ошибка API: {str(e)}. Используется локальный расчет.")

            # Fallback: локальный расчет цены
            if stattrak:
                if skin_info['stattrak_prices'] and condition in skin_info['stattrak_prices']:
                    actual_price = skin_info['stattrak_prices'][condition]
                else:
                    actual_price = None
            else:
                if condition in skin_info['prices']:
                    actual_price = skin_info['prices'][condition]
                else:
                    actual_price = None

            predicted_price = actual_price if actual_price else skin_info['factory_new_price']

            if predicted_price:
                return {
                    'predicted_price': predicted_price,
                    'actual_price': actual_price,
                    'weapon': weapon,
                    'skin': skin_name,
                    'rarity': skin_info['rarity'],
                    'condition': condition,
                    'stattrak': stattrak,
                    'min_wear': skin_info['min_wear'],
                    'max_wear': skin_info['max_wear'],
                    'source': 'database'
                }
            else:
                # Расчет на основе похожих скинов
                similar_skins = self.df_skins[
                    (self.df_skins['Weapon'] == weapon) &
                    (self.df_skins['Rarity'] == skin_info['rarity'])
                    ]

                if len(similar_skins) > 0:
                    avg_price = similar_skins['Factory New'].mean()
                    predicted_price = avg_price
                else:
                    rarity_prices = {
                        'Contraband': 1000.0,
                        'Covert': 150.0,
                        'Classified': 75.0,
                        'Restricted': 30.0,
                        'Mil-Spec': 15.0,
                        'Industrial Grade': 8.0,
                        'Consumer Grade': 3.0
                    }
                    predicted_price = rarity_prices.get(skin_info['rarity'], 25.0)

                return {
                    'predicted_price': predicted_price,
                    'actual_price': None,
                    'weapon': weapon,
                    'skin': skin_name,
                    'rarity': skin_info['rarity'],
                    'condition': condition,
                    'stattrak': stattrak,
                    'source': 'estimated'
                }
        else:
            # Скин не найден
            all_skins = self.df_skins[self.df_skins['Weapon'] == weapon]['Case'].tolist()
            matches = get_close_matches(skin_name, all_skins, n=3, cutoff=0.6)

            if matches:
                return {
                    'predicted_price': None,
                    'actual_price': None,
                    'weapon': weapon,
                    'skin': skin_name,
                    'suggestions': matches,
                    'error': 'not_found'
                }
            else:
                return {
                    'predicted_price': None,
                    'actual_price': None,
                    'weapon': weapon,
                    'skin': skin_name,
                    'error': 'not_found'
                }

    def get_price_comparison(self, weapon, skin_name):
        """Получить сравнение цен для разных состояний"""
        skin_info = self.get_skin_info(weapon, skin_name)

        if skin_info:
            return {
                'weapon': weapon,
                'skin': skin_name,
                'prices': skin_info['prices'],
                'stattrak_prices': skin_info['stattrak_prices']
            }
        return None

    def search_skins(self, query):
        """Поиск скинов по названию"""
        if self.df_skins is None:
            return []

        mask = self.df_skins['Case'].str.contains(query, case=False, na=False)
        results = self.df_skins[mask][['Weapon', 'Case', 'Rarity', 'Factory New']].copy()
        results = results.drop_duplicates(subset=['Weapon', 'Case'])

        return results.to_dict('records')


# Создаем глобальный экземпляр предсказателя
@st.cache_resource
def get_predictor():
    """Создание и кэширование предсказателя"""
    predictor = SkinPricePredictor()
    predictor.load_models()
    return predictor