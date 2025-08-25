"""Client pour récupérer les données de l'API Ligue1+"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from config import LIGUE1_API_BASE, LIGUE1_API_ENDPOINT, TIMEZONE

class Ligue1ApiClient:
    """Client pour l'API Ligue1+"""
    
    def __init__(self):
        self.base_url = LIGUE1_API_BASE
        self.endpoint = LIGUE1_API_ENDPOINT
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_matches(self, from_date: str, days_limit: int = 7, look_after: bool = True) -> Optional[Dict[str, Any]]:
        """
        Récupère les matchs depuis l'API
        
        Args:
            from_date: Date de début au format YYYY-MM-DD
            days_limit: Nombre de jours à récupérer
            look_after: Si True, récupère les matchs après la date
        
        Returns:
            Dict contenant les données de l'API ou None si erreur
        """
        params = {
            'fromDate': from_date,
            'timezone': TIMEZONE,
            'daysLimit': days_limit,
            'lookAfter': str(look_after).lower()
        }
        
        try:
            url = f"{self.base_url}{self.endpoint}"
            logging.info(f"Fetching matches from: {url}")
            logging.info(f"Parameters: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logging.info(f"Retrieved {len(data.get('results', {}).get('matches', {}))} matches")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur lors de la récupération des données: {e}")
            return None
        except ValueError as e:
            logging.error(f"Erreur lors du parsing JSON: {e}")
            return None
    
    def get_matches_for_period(self, start_date: datetime, end_date: datetime) -> Optional[Dict[str, Any]]:
        """
        Récupère les matchs pour une période donnée
        
        Args:
            start_date: Date de début
            end_date: Date de fin
        
        Returns:
            Dict contenant tous les matchs de la période
        """
        all_matches = {}
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            data = self.get_matches(date_str, days_limit=1)
            
            if data and 'results' in data and 'matches' in data['results']:
                all_matches.update(data['results']['matches'])
            
            current_date += timedelta(days=1)
        
        return {
            'results': {
                'matches': all_matches
            }
        } if all_matches else None
