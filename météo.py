#Fonction pour interroger l'API OpenWeatherMap (/forecast)
from asyncio import wait
import requests
def get_weather(api_key, city):
    """
    Interroge l'API OpenWeatherMap pour obtenir les prévisions météorologiques.
    :param api_key: Clé API pour accéder à l'API OpenWeatherMap.
    :param city: Nom de la ville pour laquelle obtenir les prévisions.
    :return: Données météorologiques au format JSON ou None en cas d'erreur.
    """
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric',
        'lang': 'fr'
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    if response.status_code == 404:
        print("Ville non trouvée.")
        return None
    if response.status_code == 401:
        print("Clé API invalide.")
        return None
    if response.status_code == 429:
        print("Limite de requête atteinte.")
        wait.sleep(60)
        return get_weather(api_key, city)
    if response.status_code == 400:
        print("Requête invalide.")
        return None
    if response.status_code == 500:
        print("Erreur serveur.")
        return None
    if response.status_code == 503:
        print("Service indisponible.")
        return None
    else:
        print(f"Erreur lors de la récupération des données météorologiques: {response.status_code}")
        return None


# Exemple d'utilisation
api_key = "5313de5c4de40cb985381e46d6b9fea8"
city1 = "Paris"
city2 = "Lyon"

# Récupération des données pour deux villes
weather_data1 = get_weather(api_key, city1)
weather_data2 = get_weather(api_key, city2)

# Fonction pour extraire les données

def extract_weather_data(weather_data):
    """
    Extrait les horodatages et les températures des données météorologiques.
    :param weather_data: Données météorologiques au format JSON.
    :return: Deux listes contenant les horodatages et les températures.
    """
    temps = []
    valeurs = []
    if weather_data:
        for forecast in weather_data['list']:
            temps.append(forecast['dt_txt'])
            valeurs.append(forecast['main']['temp'])
    return temps, valeurs

# Extraction des données pour chaque ville
if weather_data1:
    temps1, valeurs1 = extract_weather_data(weather_data1)
    print(f"Prévisions pour {city1}:")
    print(temps1)
    print(valeurs1)

if weather_data2:
    temps2, valeurs2 = extract_weather_data(weather_data2)
    print(f"Prévisions pour {city2}:")
    print(temps2)
    print(valeurs2)
