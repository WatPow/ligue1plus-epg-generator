"""Script principal pour générer l'EPG Ligue1+"""

import logging
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from api_client import Ligue1ApiClient
from match_parser import MatchParser
from xml_generator import XMLTVGenerator
from config import EPG_OUTPUT_FILE

def setup_logging(verbose: bool = False) -> None:
    """Configure le logging"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def generate_epg(days_ahead: int = 7, output_file: str = None, verbose: bool = False) -> bool:
    """
    Génère l'EPG pour Ligue1+
    
    Args:
        days_ahead: Nombre de jours à récupérer à partir d'aujourd'hui
        output_file: Fichier de sortie (optionnel)
        verbose: Mode verbose
    
    Returns:
        True si succès, False sinon
    """
    setup_logging(verbose)
    
    if output_file is None:
        output_file = EPG_OUTPUT_FILE
    
    try:
        logging.info("=== Début de la génération EPG Ligue1+ ===")
        
        # Initialiser les composants
        api_client = Ligue1ApiClient()
        parser = MatchParser()
        xml_generator = XMLTVGenerator()
        
        # Calculer les dates
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=days_ahead)
        
        logging.info(f"Récupération des matchs du {start_date} au {end_date}")
        
        # Récupérer les données
        api_data = api_client.get_matches_for_period(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.min.time())
        )
        
        if not api_data:
            logging.error("Impossible de récupérer les données de l'API")
            return False
        
        # Parser les matchs
        matches = parser.parse_matches(api_data)
        
        if not matches:
            logging.warning("Aucun match Ligue1+ trouvé pour la période")
            # On génère quand même un EPG vide
        
        # Générer le XML
        xml_content = xml_generator.generate_epg(matches)
        
        # Sauvegarder
        xml_generator.save_to_file(xml_content, output_file)
        
        logging.info(f"=== EPG généré avec succès: {output_file} ===")
        logging.info(f"Nombre de programmes: {len(matches)}")
        
        # Afficher un résumé des matchs
        if matches and verbose:
            logging.info("=== Résumé des matchs ===")
            for match in matches:
                logging.info(f"  {match.start_time.strftime('%d/%m %H:%M')} - {match.title}")
        
        return True
        
    except Exception as e:
        logging.error(f"Erreur lors de la génération EPG: {e}")
        if verbose:
            logging.exception("Détails de l'erreur:")
        return False

def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description="Générateur EPG pour Ligue1+",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python epg_generator.py                    # EPG pour 7 jours
  python epg_generator.py -d 14              # EPG pour 14 jours  
  python epg_generator.py -o my_epg.xml      # Fichier de sortie personnalisé
  python epg_generator.py -v                 # Mode verbose
        """
    )
    
    parser.add_argument(
        '-d', '--days',
        type=int,
        default=7,
        help='Nombre de jours à récupérer (défaut: 7)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help=f'Fichier de sortie (défaut: {EPG_OUTPUT_FILE})'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Mode verbose'
    )
    
    args = parser.parse_args()
    
    # Valider les arguments
    if args.days <= 0:
        print("Erreur: Le nombre de jours doit être positif")
        sys.exit(1)
    
    if args.days > 30:
        print("Attention: Plus de 30 jours peuvent prendre du temps")
    
    # Générer l'EPG
    success = generate_epg(
        days_ahead=args.days,
        output_file=args.output,
        verbose=args.verbose
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
