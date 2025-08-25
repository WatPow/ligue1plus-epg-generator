"""Générateur XML pour l'EPG au format XMLTV"""

import logging
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
from lxml import etree
from match_parser import MatchData
from config import CHANNEL_ID, CHANNEL_NAME

class XMLTVGenerator:
    """Générateur EPG au format XMLTV"""
    
    def __init__(self):
        self.channel_id = CHANNEL_ID
        self.channel_name = CHANNEL_NAME
    
    def generate_epg(self, matches: List[MatchData]) -> str:
        """
        Génère l'EPG XML au format XMLTV
        
        Args:
            matches: Liste des matchs à inclure
        
        Returns:
            String contenant le XML généré
        """
        # Créer l'élément racine
        root = etree.Element("tv")
        
        # Ajouter le canal
        self._add_channel(root)
        
        # Grouper les matchs par créneaux horaires et gérer les multiplex
        programmes = self._create_programmes_with_multiplex(matches)
        
        # Ajouter les programmes
        for programme in programmes:
            self._add_programme_element(root, programme)
        
        # Convertir en string avec formatage
        xml_string = etree.tostring(
            root, 
            encoding='utf-8', 
            xml_declaration=True, 
            pretty_print=True
        ).decode('utf-8')
        
        logging.info(f"Generated EPG XML with {len(programmes)} programmes")
        return xml_string
    
    def _add_channel(self, root: etree.Element) -> None:
        """Ajoute la définition du canal"""
        channel = etree.SubElement(root, "channel", id=self.channel_id)
        
        # Nom d'affichage principal
        display_name = etree.SubElement(channel, "display-name")
        display_name.text = self.channel_name
        
        # Nom d'affichage alternatif
        display_name_alt = etree.SubElement(channel, "display-name")
        display_name_alt.text = "Ligue1Plus"
        
        # URL du logo (si disponible)
        icon = etree.SubElement(channel, "icon", 
                               src="https://ligue1plus.fr/favicon.ico")
    
    def _create_programmes_with_multiplex(self, matches: List[MatchData]) -> List[Dict[str, Any]]:
        """
        Crée les programmes en gérant les multiplex pour les matchs simultanés
        
        Args:
            matches: Liste des matchs
        
        Returns:
            Liste des programmes (matchs individuels ou multiplex)
        """
        # Grouper les matchs par créneau horaire
        time_groups = defaultdict(list)
        
        for match in matches:
            # Utiliser start_time comme clé de regroupement
            time_key = match.start_time.strftime("%Y%m%d%H%M")
            time_groups[time_key].append(match)
        
        programmes = []
        
        for time_key, group_matches in time_groups.items():
            if len(group_matches) == 1:
                # Match unique, programme normal
                match = group_matches[0]
                programmes.append({
                    'type': 'single',
                    'match': match,
                    'start_time': match.start_time,
                    'end_time': match.end_time,
                    'title': match.title,
                    'description': match.description,
                    'championship': match.championship,
                    'home_team': match.home_team,
                    'away_team': match.away_team
                })
            else:
                # Plusieurs matchs simultanés, créer un multiplex
                multiplex_programme = self._create_multiplex_programme(group_matches)
                programmes.append(multiplex_programme)
        
        # Trier par heure de début
        programmes.sort(key=lambda x: x['start_time'])
        
        logging.info(f"Created {len(programmes)} programmes from {len(matches)} matches")
        for prog in programmes:
            if prog['type'] == 'multiplex':
                logging.info(f"  Multiplex: {len(prog['matches'])} matchs simultanés à {prog['start_time'].strftime('%d/%m %H:%M')}")
        
        return programmes
    
    def _create_multiplex_programme(self, matches: List[MatchData]) -> Dict[str, Any]:
        """
        Crée un programme multiplex pour des matchs simultanés
        
        Args:
            matches: Liste des matchs simultanés
        
        Returns:
            Dict représentant le programme multiplex
        """
        # Prendre les temps du premier match (ils sont identiques)
        start_time = matches[0].start_time
        end_time = matches[0].end_time
        championship = matches[0].championship
        
        # Créer le titre multiplex
        match_list = []
        for match in matches:
            match_list.append(f"{match.home_team} vs {match.away_team}")
        
        title = f"{championship} - Multiplex"
        
        # Description détaillée
        description_parts = ["Multiplex :"]
        for i, match in enumerate(matches, 1):
            description_parts.append(f"{i}. {match.home_team} vs {match.away_team}")
        
        description = " ".join(description_parts)
        
        return {
            'type': 'multiplex',
            'matches': matches,
            'start_time': start_time,
            'end_time': end_time,
            'title': title,
            'description': description,
            'championship': championship,
            'home_team': None,  # Pas applicable pour multiplex
            'away_team': None   # Pas applicable pour multiplex
        }
    
    def _add_programme_element(self, root: etree.Element, programme_data: Dict[str, Any]) -> None:
        """Ajoute un programme (match ou multiplex) à l'EPG"""
        
        # Formatage des dates XMLTV (YYYYMMDDHHMMSS +HHMM)
        start_time = self._format_xmltv_time(programme_data['start_time'])
        stop_time = self._format_xmltv_time(programme_data['end_time'])
        
        # Créer l'élément programme
        programme = etree.SubElement(
            root, 
            "programme",
            start=start_time,
            stop=stop_time,
            channel=self.channel_id
        )
        
        # Titre
        title = etree.SubElement(programme, "title", lang="fr")
        title.text = programme_data['title']
        
        # Description
        desc = etree.SubElement(programme, "desc", lang="fr")
        desc.text = programme_data['description']
        
        # Catégories
        category_sport = etree.SubElement(programme, "category", lang="fr")
        category_sport.text = "Sport"
        
        category_football = etree.SubElement(programme, "category", lang="fr")
        category_football.text = "Football"
        
        if programme_data['championship']:
            category_championship = etree.SubElement(programme, "category", lang="fr")
            category_championship.text = programme_data['championship']
        
        # Gestion différente selon le type de programme
        if programme_data['type'] == 'single':
            # Match individuel - crédit avec équipes
            credits = etree.SubElement(programme, "credits")
            
            presenter_home = etree.SubElement(credits, "presenter")
            presenter_home.text = programme_data['home_team']
            
            guest_away = etree.SubElement(credits, "guest")
            guest_away.text = programme_data['away_team']
            
        elif programme_data['type'] == 'multiplex':
            # Multiplex - crédit avec tous les matchs
            credits = etree.SubElement(programme, "credits")
            
            for match in programme_data['matches']:
                presenter = etree.SubElement(credits, "presenter")
                presenter.text = f"{match.home_team} vs {match.away_team}"
            
            # Catégorie spéciale pour multiplex
            category_multiplex = etree.SubElement(programme, "category", lang="fr")
            category_multiplex.text = "Multiplex"
        
        # Épisode/Numéro du match (basé sur la date)
        episode_num = etree.SubElement(programme, "episode-num", system="original-air-date")
        episode_num.text = programme_data['start_time'].strftime("%Y-%m-%d")
        
        # Rating (tous publics pour le sport)
        rating = etree.SubElement(programme, "rating", system="MPAA")
        rating_value = etree.SubElement(rating, "value")
        rating_value.text = "G"
    
    def _format_xmltv_time(self, dt: datetime) -> str:
        """
        Formate une datetime au format XMLTV
        Format: YYYYMMDDHHMMSS +HHMM
        """
        # Convertir en temps local avec offset
        timestamp = dt.strftime("%Y%m%d%H%M%S")
        
        # Calculer l'offset timezone
        offset = dt.strftime("%z")
        if not offset:
            # Si pas d'info timezone, utiliser +0100 par défaut (heure française)
            offset = "+0100"
        else:
            # Reformater l'offset si nécessaire
            if len(offset) == 5:  # Format +0100 déjà correct
                pass
            elif len(offset) == 3:  # Format +01
                offset = offset + "00"
        
        return f"{timestamp} {offset}"
    
    def save_to_file(self, xml_content: str, filename: str) -> None:
        """Sauvegarde l'EPG dans un fichier"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            logging.info(f"EPG sauvegardé dans {filename}")
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde: {e}")
            raise
