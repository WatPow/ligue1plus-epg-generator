# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

## [1.0.0] - 2025-08-25

### ✨ Ajouté
- Récupération automatique des matchs via l'API officielle Ligue1
- Génération d'EPG au format XMLTV standard
- Gestion intelligente des multiplex pour les matchs simultanés
- Configuration flexible via fichier config.py
- Options en ligne de commande (durée, fichier de sortie, mode verbose)
- Logs détaillés pour monitoring et debug
- Documentation complète avec exemples d'intégration IPTV
- Support automatisation via tâches planifiées
- Filtrage automatique des matchs diffusés sur Ligue1+

### 🔧 Fonctionnalités techniques
- Client API robuste avec gestion d'erreurs
- Parser intelligent des données de matchs
- Générateur XML conforme aux standards XMLTV
- Gestion des timezones (Europe/Paris)
- Détection automatique des conflits horaires
- Regroupement des matchs simultanés en programmes multiplex

### 📺 Format de sortie
- Canal Ligue1+ avec métadonnées complètes
- Programmes avec titre, description, catégories
- Informations sur les équipes (presenter/guest)
- Ratings et numéros d'épisode
- Catégorie spéciale "Multiplex" pour les diffusions simultanées

### 🎯 Compatibilité
- Python 3.7+
- Lecteurs IPTV : Kodi, VLC, Perfect Player, TiviMate, GSE Smart IPTV
- Plateformes : Windows, Linux, macOS
- Format : XMLTV standard
