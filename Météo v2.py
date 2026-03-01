import time
import requests
import matplotlib.pyplot as plt
import folium
import webbrowser
import os
import base64
import io

def get_weather(api_key, city):
    """
    Interroge l'API OpenWeatherMap pour obtenir les prévisions météo.
    
    IN: api_key -> str: Clé API OpenWeatherMap
        city -> str: Nom de la ville
    OUT: dict ou None: Données JSON de l'API ou None en cas d'erreur
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
    
    IN: weather_data -> dict: Données JSON retournées par l'API
    OUT: tuple: (temps, valeurs) - Listes des dates/heures et températures
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
    
    IN: date_str -> str: Date au format 'YYYY-MM-DD HH:MM:SS'
    OUT: str: Date formatée 'JJ/MM/AA-HH:MM'
    """
    annee = date_str[2:4]
    mois = date_str[5:7]
    jour = date_str[8:10]
    heure = date_str[11:16]
    
    return f"{jour}/{mois}/{annee}-{heure}"


def creer_courbe(ville, temps, valeurs):
    """
    Crée un graphique Matplotlib et le retourne encodé en base64.
    
    IN: ville -> str: Nom de la ville
        temps -> list: Liste des dates et horaires
        valeurs -> list: Liste des températures
    OUT: str: Image encodée en base64
    
    Description:
        Génère un diagramme de l'évolution des températures
        et retourne l'image directement en base64 (sans fichier temporaire)
    """
    
    # Formatage des dates
    temps_formates = [formater_date(t) for t in temps]
    
    # Calcul de la température maximale
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
    
    # Légende en arrière-plan
    legend = ax.legend(
        [plt.Line2D([0], [0], color='red', linestyle='--', alpha=0.4)],
        [f'Max: {temp_max:.1f}°C'],
        loc='upper right',
        framealpha=0.5,
        facecolor='white'
    )
    legend.set_zorder(0)
    
    # Rotation des étiquettes de dates
    plt.xticks(rotation=45, ha="right", fontsize=8)
    
    # Afficher une étiquette sur deux
    for i, label in enumerate(ax.xaxis.get_ticklabels()):
        if i % 2 != 0:
            label.set_visible(False)
    
    ax.margins(x=0.02)
    plt.tight_layout()
    
    # ====================================================================
    # EXPORT DIRECT EN BASE64 (sans fichier temporaire sur le disque)
    # ====================================================================
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()  # Libération de la mémoire
    
    print(f"✓ Graphique généré pour {ville}")
    print(f"  → Température max: {temp_max:.1f}°C")
    
    return encoded  # Retourne directement l'image en base64


# ====================
# PROGRAMME PRINCIPAL
# ====================

# Clé API (À REMPLACER PAR LA VÔTRE)
api_key = "5313de5c4de40cb985381e46d6b9fea8"

# Liste des 5 villes à afficher
villes = ["Paris", "Lyon", "Toulouse", "Marseille", "Lille"]

# Dictionnaire pour stocker les images base64
images_base64 = {}

print("=" * 50)
print("   RÉCUPÉRATION DES PRÉVISIONS MÉTÉO")
print("=" * 50)

# Récupération et traitement des données pour chaque ville
for ville in villes:
    print(f"\n📍 Traitement de {ville}...")
    
    weather_data = get_weather(api_key, ville)
    
    if weather_data:
        temps, valeurs = extract_weather_data(weather_data)
        
        if temps and valeurs:
            # Génération du graphique et récupération du base64
            encoded_image = creer_courbe(ville, temps, valeurs)
            images_base64[ville] = encoded_image
        else:
            print(f"  ✗ Pas de données disponibles pour {ville}")
    else:
        print(f"  ✗ Échec de récupération pour {ville}")

print("\n" + "=" * 50)
print("   CRÉATION DE LA CARTE FOLIUM")
print("=" * 50)

# ====================================================================
# CRÉATION DE LA CARTE CENTRÉE SUR LA FRANCE
# ====================================================================
ma_carte = folium.Map(
    location=[46.6, 1.8],      # Centre de la France
    tiles="OpenStreetMap",     # Style de carte
    zoom_start=6               # Niveau de zoom adapté
)

# ====================================================================
# INFORMATIONS DES VILLES (coordonnées + icônes personnalisées)
# ====================================================================
cities_info = {
    "Paris":     {"coords": [48.8566, 2.3522], "icon": "archway",      "icon_color": "navajowhite"},
    "Marseille": {"coords": [43.2965, 5.3698], "icon": "sun",          "icon_color": "yellow"},
    "Lyon":      {"coords": [45.7640, 4.8357], "icon": "synagogue",    "icon_color": "white"},
    "Toulouse":  {"coords": [43.6047, 1.4442], "icon": "bridge-water", "icon_color": "mediumaquamarine"},
    "Lille":     {"coords": [50.6292, 3.0573], "icon": "chess-rook",   "icon_color": "navajowhite"},
}

# ====================================================================
# AJOUT DES 5 MARQUEURS AVEC TOOLTIP (SURVOL) ET ICÔNES PERSONNALISÉES
# ====================================================================
for ville, info in cities_info.items():
    if ville in images_base64:
        # Récupération de l'image base64
        encoded = images_base64[ville]
        
        # Construction du HTML pour le tooltip
        img_tag = f'<img src="data:image/png;base64,{encoded}" style="width:500px;height:auto;">'
        html = f'<div style="font-family: Arial; text-align: center;"><h3>{ville}</h3>{img_tag}</div>'
        
        # ====================================================================
        # TOOLTIP (AFFICHAGE AU SURVOL) - CRITÈRE PRINCIPAL DU SUJET
        # ====================================================================
        tooltip = folium.Tooltip(html, sticky=True)
        
        # ====================================================================
        # MARQUEUR AVEC ICÔNE FONT AWESOME PERSONNALISÉE
        # ====================================================================
        folium.Marker(
            location=info["coords"],
            tooltip=tooltip,  # ← SURVOL (pas popup !)
            icon=folium.Icon(
                icon=info["icon"],           # Icône Font Awesome
                prefix='fa',                 # Préfixe Font Awesome
                color='darkred',             # Couleur du marqueur
                icon_color=info["icon_color"] # Couleur de l'icône
            )
        ).add_to(ma_carte)

# ====================================================================
# SAUVEGARDE DE LA CARTE HTML
# ====================================================================
chemin_carte = os.path.abspath("carte_meteo.html")
ma_carte.save(chemin_carte)
print(f"\n✓ Carte sauvegardée : {chemin_carte}")

# Ouverture automatique dans le navigateur
webbrowser.open('file://' + chemin_carte)
