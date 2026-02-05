import time
import requests


def get_weather(api_key, city):
    """
    Interroge l'API OpenWeatherMap pour obtenir les prévisions météo.

    Paramètres
    - api_key (str) : clé API OpenWeatherMap.
    - city (str) : nom de la ville (ex. 'Paris' ou 'Lyon').

    Retour
    - dict : objet JSON de la réponse si tout s'est bien passé (status 200).
    - None : en cas d'erreur ou si la requête ne peut pas être satisfaite.

    Remarques
    - L'URL utilisée est l'endpoint `forecast` qui renvoie des prévisions
      toutes les 3 heures pour les prochains jours.
    - La fonction gère plusieurs codes HTTP et affiche un message utile
      pour l'utilisateur en cas d'erreur.
    - En cas de `429 Too Many Requests`, la fonction attend 60 secondes
      puis retente automatiquement (récursion simple). Cela évite une
      exception due à l'utilisation incorrecte de `asyncio.wait`.
    """
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        'q': city,            # ville demandée
        'appid': api_key,     # clé API
        'units': 'metric',    # températures en °C
        'lang': 'fr'          # langue des descriptions
    }

    # Effectue la requête HTTP GET vers l'API
    response = requests.get(base_url, params=params)

    # Code 200 : succès, on renvoie le JSON
    if response.status_code == 200:
        return response.json()

    # Gestion des erreurs utilisateur/serveur courantes
    if response.status_code == 404:
        print("Ville non trouvée.")
        return None

    if response.status_code == 401:
        print("Clé API invalide.")
        return None

    # Trop de requêtes : on attend un peu puis on retente
    if response.status_code == 429:
        print("Limite de requête atteinte. Attente de 60 secondes avant réessai.")
        time.sleep(60)
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

    # Pour tout autre code inattendu
    print(f"Erreur lors de la récupération des données météorologiques: {response.status_code}")
    return None


# Exemple d'utilisation basique
# Remplacez `api_key` par votre propre clé si nécessaire.
api_key = "5313de5c4de40cb985381e46d6b9fea8"
city1 = "Paris"
city2 = "Lyon"

# Récupération des données pour deux villes
weather_data1 = get_weather(api_key, city1)
weather_data2 = get_weather(api_key, city2)


def extract_weather_data(weather_data):
    """
    Extrait deux listes à partir du JSON de prévision OpenWeatherMap :
    - `temps` : liste d'horodatages (chaînes) fournis par `dt_txt`.
    - `valeurs` : liste des températures en °C pour chaque horodatage.

    Structure attendue de `weather_data` (extrait) :
    {
        'list': [
            {
                'dt_txt': '2026-02-05 12:00:00',
                'main': {'temp': 5.0},
                ...
            },
            ...
        ]
    }

    Retourne deux listes vides si `weather_data` est None.
    """
    temps = []     # horodatages (ex. '2026-02-05 12:00:00')
    valeurs = []   # températures correspondantes (float en °C)

    if weather_data:
        # `list` contient les prévisions (généralement toutes les 3 heures)
        for forecast in weather_data.get('list', []):
            # Sécurise l'accès aux champs attendus
            dt = forecast.get('dt_txt')
            temp = None
            main = forecast.get('main')
            if main:
                temp = main.get('temp')

            if dt is not None and temp is not None:
                temps.append(dt)
                valeurs.append(temp)

    return temps, valeurs


# Extraction et affichage des données pour chaque ville (si disponibles)
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
