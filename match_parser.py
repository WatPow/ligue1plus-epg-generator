"""Parser pour extraire et traiter les données des matchs"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dateutil import parser as date_parser
from config import TARGET_BROADCASTER, DEFAULT_MATCH_DURATION

class MatchData:
    """Classe pour représenter un match"""
    
    def __init__(self, match_id: str, home_team: str, away_team: str, 
                 start_time: datetime, end_time: datetime, 
                 title: str, description: str, championship: str = ""):
        self.match_id = match_id
        self.home_team = home_team
        self.away_team = away_team
        self.start_time = start_time
        self.end_time = end_time
        self.title = title
        self.description = description
        self.championship = championship

class MatchParser:
    """Parser pour les données de matchs Ligue1+"""
    
    def __init__(self):
        self.target_broadcaster = TARGET_BROADCASTER
    
    def parse_matches(self, api_data: Dict[str, Any]) -> List[MatchData]:
        """
        Parse les données de l'API et retourne les matchs diffusés sur Ligue1+
        
        Args:
            api_data: Données de l'API
        
        Returns:
            Liste des matchs formatés
        """
        matches = []
        
        if not api_data or 'results' not in api_data:
            logging.warning("Pas de données de résultats dans la réponse API")
            return matches
        
        api_matches = api_data['results'].get('matches', {})
        
        for match_id, match_data in api_matches.items():
            try:
                # Vérifier si le match est diffusé sur Ligue1+
                if not self._is_ligue1_plus_match(match_data):
                    continue
                
                parsed_match = self._parse_single_match(match_id, match_data)
                if parsed_match:
                    matches.append(parsed_match)
                    
            except Exception as e:
                logging.error(f"Erreur lors du parsing du match {match_id}: {e}")
                continue
        
        # Trier par heure de début
        matches.sort(key=lambda x: x.start_time)
        
        logging.info(f"Parsed {len(matches)} Ligue1+ matches")
        return matches
    
    def _is_ligue1_plus_match(self, match_data: Dict[str, Any]) -> bool:
        """Vérifie si le match est diffusé sur Ligue1+"""
        broadcasters = match_data.get('broadcasters', {})
        local_broadcasters = broadcasters.get('local', [])
        
        for broadcaster in local_broadcasters:
            if broadcaster.get('code') == self.target_broadcaster:
                return True
        
        return False
    
    def _parse_single_match(self, match_id: str, match_data: Dict[str, Any]) -> Optional[MatchData]:
        """Parse un match individuel"""
        try:
            # Extraire les équipes
            home_team = self._extract_team_name(match_data.get('home', {}))
            away_team = self._extract_team_name(match_data.get('away', {}))
            
            # Extraire les temps
            match_date_str = match_data.get('date')
            if not match_date_str:
                logging.warning(f"Pas de date pour le match {match_id}")
                return None
            
            start_time = date_parser.parse(match_date_str)
            # Durée par défaut du match
            end_time = start_time + timedelta(minutes=DEFAULT_MATCH_DURATION)
            
            # Créer le titre et la description
            championship_info = self._get_championship_info(match_data)
            base_title = f"{home_team} vs {away_team}"
            
            if championship_info:
                base_title = f"{championship_info} - {base_title}"
            
            # Ajouter un préfixe selon le statut temporel
            title = self._add_temporal_prefix(base_title, start_time, match_data)
            
            description = self._create_description(match_data, home_team, away_team, championship_info)
            
            return MatchData(
                match_id=match_id,
                home_team=home_team,
                away_team=away_team,
                start_time=start_time,
                end_time=end_time,
                title=title,
                description=description,
                championship=championship_info
            )
            
        except Exception as e:
            logging.error(f"Erreur lors du parsing du match {match_id}: {e}")
            return None
    
    def _extract_team_name(self, team_data: Dict[str, Any]) -> str:
        """Extrait le nom de l'équipe"""
        club_identity = team_data.get('clubIdentity', {})
        
        # Essayer différents champs pour le nom
        for field in ['displayName', 'name', 'shortName', 'officialName']:
            name = club_identity.get(field)
            if name:
                return name
        
        return "Équipe inconnue"
    
    def _get_championship_info(self, match_data: Dict[str, Any]) -> str:
        """Récupère les informations du championnat"""
        championship_id = match_data.get('championshipId')
        game_week = match_data.get('gameWeekNumber')
        
        championship_names = {
            1: "Ligue 1",
            4: "Ligue 2"
        }
        
        championship_name = championship_names.get(championship_id, "Championnat")
        
        if game_week:
            return f"{championship_name} - J{game_week}"
        
        return championship_name
    
    def _create_description(self, match_data: Dict[str, Any], home_team: str, 
                          away_team: str, championship: str) -> str:
        """Crée la description du match"""
        description_parts = []
        
        if championship:
            description_parts.append(f"Match de {championship}")
        
        description_parts.append(f"{home_team} reçoit {away_team}")
        
        return " - ".join(description_parts)
    
    def _add_temporal_prefix(self, base_title: str, match_time: datetime, match_data: Dict[str, Any]) -> str:
        """
        Ajoute un préfixe au titre selon le statut temporel du match
        
        Args:
            base_title: Titre de base du match
            match_time: Heure du match
            match_data: Données du match pour vérifier le statut live
        
        Returns:
            Titre avec préfixe approprié
        """
        from datetime import datetime, timezone
        
        # Vérifier si le match est en direct
        is_live = match_data.get('isLive', False)
        period = match_data.get('period', 'preMatch')
        
        if is_live or period == 'live':
            # Match en direct - pas de préfixe
            return base_title
        
        # Calculer la différence avec maintenant (en UTC)
        now = datetime.now(timezone.utc)
        match_utc = match_time.replace(tzinfo=timezone.utc)
        time_diff = match_utc - now
        
        if period == 'postMatch' or time_diff.total_seconds() < -7200:  # Plus de 2h passées
            # Match terminé
            return f"[TERMINÉ] {base_title}"
        elif time_diff.total_seconds() < 0:
            # Match commencé mais pas marqué live (problème API)
            return base_title
        elif time_diff.total_seconds() < 3600:  # Moins d'1h
            # Match très proche
            return f"[IMMINENT] {base_title}"
        elif time_diff.days == 0:
            # Match aujourd'hui
            return f"[AUJOURD'HUI] {base_title}"
        elif time_diff.days <= 1:
            # Match demain
            return f"[DEMAIN] {base_title}"
        else:
            # Match à venir
            return f"[PROCHAIN MATCH] {base_title}"
