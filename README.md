# 📺 Ligue1+ EPG Generator

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![XMLTV](https://img.shields.io/badge/Format-XMLTV-orange)](http://xmltv.org/)

Générateur d'EPG (Electronic Program Guide) au format XMLTV pour la chaîne **Ligue1+**, utilisant l'API officielle de la Ligue de Football Professionnel.

## ✨ Fonctionnalités

- 🔄 **Récupération automatique** des matchs depuis l'API officielle Ligue1
- 📺 **Format XMLTV** standard compatible avec tous les lecteurs IPTV
- 🔀 **Gestion des multiplex** pour les matchs simultanés
- ⚙️ **Configuration flexible** et options en ligne de commande
- 📝 **Logs détaillés** pour monitoring et debug
- 🕒 **Automatisation** via tâches planifiées

## 🚀 Installation

```bash
git clone https://github.com/votre-username/ligue1-epg-generator.git
cd ligue1-epg-generator
pip install -r requirements.txt
```

## 💻 Utilisation

### Usage basique
```bash
python epg_generator.py
```

### Options avancées
```bash
# EPG pour 14 jours
python epg_generator.py -d 14

# Fichier de sortie personnalisé
python epg_generator.py -o mon_epg.xml

# Mode verbose pour debug
python epg_generator.py -v

# Combinaison d'options
python epg_generator.py -d 14 -o epg_2_semaines.xml -v
```

## ⚙️ Configuration

Modifiez `config.py` pour personnaliser :
- ID et nom du canal
- Durée par défaut des matchs
- Nom du fichier de sortie
- Paramètres de l'API

```python
# Configuration du canal
CHANNEL_ID = "Ligue1Plus"
CHANNEL_NAME = "Ligue 1+"

# Configuration de sortie
EPG_OUTPUT_FILE = "ligue1_epg.xml"
DEFAULT_MATCH_DURATION = 120  # minutes
```

## 📁 Structure du projet

```
ligue1-epg-generator/
├── 📄 config.py          # Configuration principale
├── 🌐 api_client.py       # Client API Ligue1
├── 🔍 match_parser.py     # Parser des données de matchs
├── 📺 xml_generator.py    # Générateur XML XMLTV
├── 🚀 epg_generator.py    # Script principal
├── 📋 requirements.txt    # Dépendances Python
├── 📖 README.md          # Documentation
└── 🙈 .gitignore         # Fichiers à ignorer
```

## 📺 Intégration IPTV

### Exemple de playlist M3U
```m3u
#EXTINF:-1 tvg-id="Ligue1Plus" tvg-name="Ligue 1+" tvg-logo="https://ligue1plus.fr/favicon.ico" group-title="Sport",Ligue 1+
http://votre-stream-ligue1plus
```

### Applications compatibles
- **Kodi** (PVR IPTV Simple Client)
- **VLC** 
- **Perfect Player**
- **TiviMate**
- **GSE Smart IPTV**

## 🔄 Automatisation

### Windows (Planificateur de tâches)
```powershell
schtasks /create /sc daily /tn "EPG Ligue1" /tr "python C:\path\to\epg_generator.py" /st 06:00
```

### Linux (Cron)
```bash
# Tous les jours à 6h du matin
0 6 * * * /usr/bin/python3 /path/to/epg_generator.py
```

### Docker (optionnel)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "epg_generator.py"]
```

## 🔀 Gestion des Multiplex

Le générateur détecte automatiquement les **matchs simultanés** et les groupe en programmes "Multiplex", reflétant fidèlement le fonctionnement de Ligue1+ :

**Exemple :**
```xml
<programme start="20250831151500 +0000" stop="20250831171500 +0000" channel="Ligue1Plus">
  <title lang="fr">Ligue 1 - J3 - Multiplex</title>
  <desc lang="fr">Multiplex : 1. Monaco vs Strasbourg 2. Le Havre vs Nice 3. Paris FC vs Metz</desc>
  <category lang="fr">Multiplex</category>
</programme>
```

## 🌐 API Source

Utilise l'API officielle de la Ligue de Football Professionnel :
```
https://ma-api.ligue1.fr/championships-daily-calendars/matches
```

## 📝 Logs et Debug

```bash
# Mode verbose pour voir les détails
python epg_generator.py -v

# Exemple de sortie
2025-08-25 13:34:12 - INFO - === Début de la génération EPG Ligue1+ ===
2025-08-25 13:34:12 - INFO - Récupération des matchs du 2025-08-25 au 2025-09-01
2025-08-25 13:34:12 - INFO - Parsed 8 Ligue1+ matches
2025-08-25 13:34:12 - INFO - Created 6 programmes from 8 matches
2025-08-25 13:34:12 - INFO -   Multiplex: 3 matchs simultanés à 31/08 15:15
2025-08-25 13:34:12 - INFO - === EPG généré avec succès: ligue1_epg.xml ===
```

## 🤝 Contributing

Les contributions sont les bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des améliorations
- 🔧 Soumettre des pull requests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ⚠️ Disclaimer

Ce projet est à des fins éducatives et personnelles. Respectez les conditions d'utilisation de l'API Ligue1 et les droits de diffusion.

---

🇫🇷 **Fait avec ❤️ pour les fainéants**
