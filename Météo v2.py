import time
import requests
import matplotlib.pyplot as plt

def get_weather(api_key, city):
    """
    Interroge l'API OpenWeatherMap pour obtenir les prévisions météo.
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
        print(f"Ville '{city}' non trouvée.")
        return None

    if response.status_code == 401:
        print("Clé API invalide.")
        return None

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

    print(f"Erreur lors de la récupération des données météorologiques: {response.status_code}")
    return None


def extract_weather_data(weather_data):
    """
    Extrait les horodatages et températures du JSON de prévision.
    """
    temps = []
    valeurs = []

    if weather_data:
        for forecast in weather_data.get('list', []):
            dt = forecast.get('dt_txt')
            temp = None
            main = forecast.get('main')
            if main:
                temp = main.get('temp')

            if dt is not None and temp is not None:
                temps.append(dt)
                valeurs.append(temp)

    return temps, valeurs


def formater_date(date_str):
    """
    Convertit '2026-02-27 18:00:00' en '27/02/26-18:00'
    """
    annee = date_str[2:4]
    mois = date_str[5:7]
    jour = date_str[8:10]
    heure = date_str[11:16]
    
    return f"{jour}/{mois}/{annee}-{heure}"


def creer_courbe(ville, temps, valeurs):
    """
    IN: ville -> str: Nom de la ville
        temps -> list: Date et horaire
        valeurs -> list: Températures
    
    Description:
        Créer un diagramme de la météo d'une
        ville et l'enregistre en format png
    """
    
    # Formatage des dates
    temps_formates = [formater_date(t) for t in temps]
    
    # Calcul de la température maximale uniquement
    temp_max = max(valeurs)
    idx_max = valeurs.index(temp_max)
    
    # Création du diagramme
    fig, ax = plt.subplots(figsize=(16, 7))
    
    # Grille en arrière-plan
    ax.grid(True, alpha=0.3, zorder=0)
    
    # Ligne horizontale pour le max (en arrière-plan)
    ax.axhline(y=temp_max, color='red', linestyle='--', alpha=0.4, zorder=1)
    
    # Courbe principale
    ax.plot(temps_formates, valeurs, marker="o", linewidth=2, markersize=4, 
            color='#1f77b4', zorder=3)
    
    # Marqueur pour la température maximale
    ax.plot(idx_max, temp_max, 'ro', markersize=10, zorder=4)
    ax.annotate(
        f'MAX: {temp_max:.1f}°C',
        xy=(idx_max, temp_max),
        xytext=(idx_max + 2, temp_max + 1),
        fontsize=10,
        fontweight='bold',
        color='red',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8),
        arrowprops=dict(arrowstyle='->', color='red'),
        zorder=5
    )
    
    # Récupération des yticks générés automatiquement
    ax.autoscale()
    fig.canvas.draw()
    yticks_originaux = [tick for tick in ax.get_yticks()]
    
    # Filtrer les yticks pour éviter la superposition avec temp_max
    seuil = (max(valeurs) - min(valeurs)) * 0.08  # 8% de la plage
    yticks_filtres = [y for y in yticks_originaux if abs(y - temp_max) > seuil]
    
    # Ajouter temp_max aux yticks
    yticks_nouveaux = sorted(yticks_filtres + [temp_max])
    ax.set_yticks(yticks_nouveaux)
    
    # Colorer le label de temp_max en rouge
    ytick_labels = ax.get_yticklabels()
    for i, tick_val in enumerate(yticks_nouveaux):
        if tick_val == temp_max:
            ytick_labels[i].set_color('red')
            ytick_labels[i].set_fontweight('bold')
    
    # Configuration du graphique
    ax.set_title(f"Prévisions météo - {ville}", fontsize=14, fontweight='bold')
    ax.set_ylabel("Températures (°C)", fontsize=11)
    ax.set_xlabel("Date et heure (JJ/MM/AA-HH:MM)", fontsize=11)
    
    # Légende en arrière-plan (zorder bas)
    legend = ax.legend(
        [plt.Line2D([0], [0], color='red', linestyle='--', alpha=0.4)],
        [f'Max: {temp_max:.1f}°C'],
        loc='upper right',
        framealpha=0.5,  # Transparence de la légende
        facecolor='white'
    )
    legend.set_zorder(0)  # Légende en arrière-plan
    
    # Rotation des étiquettes de dates
    plt.xticks(rotation=45, ha="right", fontsize=8)
    
    # Afficher une étiquette sur deux
    for i, label in enumerate(ax.xaxis.get_ticklabels()):
        if i % 2 != 0:
            label.set_visible(False)
    
    ax.margins(x=0.02)
    plt.tight_layout()
    
    # Enregistrement
    nom_fichier = f"meteo_de_{ville.replace(' ', '_')}.png"
    plt.savefig(nom_fichier, dpi=150)
    plt.close()
    
    print(f"✓ Graphique sauvegardé : {nom_fichier}")
    print(f"  → Température max: {temp_max:.1f}°C")


# ====================
# PROGRAMME PRINCIPAL
# ====================

api_key = "5313de5c4de40cb985381e46d6b9fea8"

# Liste des villes
villes = ["Paris", "Lyon", "Toulouse", "Marseille", "Lille"]

print("=" * 50)
print("   RÉCUPÉRATION DES PRÉVISIONS MÉTÉO")
print("=" * 50)

for ville in villes:
    print(f"\n📍 Traitement de {ville}...")
    
    weather_data = get_weather(api_key, ville)
    
    if weather_data:
        temps, valeurs = extract_weather_data(weather_data)
        
        if temps and valeurs:
            creer_courbe(ville, temps, valeurs)
        else:
            print(f"  ✗ Pas de données disponibles pour {ville}")
    else:
        print(f"  ✗ Échec de récupération pour {ville}")

print("\n" + "=" * 50)
print("   TRAITEMENT TERMINÉ")
print("=" * 50)
