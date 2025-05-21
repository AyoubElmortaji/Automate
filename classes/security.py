import hashlib
import csv
import os
from datetime import datetime
from pathlib import Path

class SecurityManager:
    def __init__(self):
        self.credentials_file = "Automates/automate_credentials.csv"
        Path("automates").mkdir(exist_ok=True)
        
        # Créer le fichier de credentials s'il n'existe pas
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['automate_name', 'password_hash', 'last_modified'])

    def hash_password(self, password: str) -> str:
        salt = "ENSAM_CASA_CSCC_2025"
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def save_credentials(self, automate_name: str, password: str):
        password_hash = self.hash_password(password)
        last_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Vérifier si l'automate existe déjà
        existing = self.get_credentials(automate_name)
        
        with open(self.credentials_file, 'a' if not existing else 'r+', newline='') as f:
            writer = csv.writer(f)
            if existing:
                # Mettre à jour les credentials existants
                lines = list(csv.reader(f))
                f.seek(0)
                for line in lines:
                    if line[0] == automate_name:
                        writer.writerow([automate_name, password_hash, last_modified])
                    else:
                        writer.writerow(line)
            else:
                # Ajouter de nouveaux credentials
                writer.writerow([automate_name, password_hash, last_modified])

    def get_credentials(self, automate_name: str) -> dict:
       
        with open(self.credentials_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if row[0] == automate_name:
                    return {
                        'automate_name': row[0],
                        'password_hash': row[1],
                        'last_modified': row[2]
                    }
        return None

    def verify_password(self, automate_name: str, password: str) -> bool:
        
        credentials = self.get_credentials(automate_name)
        if not credentials:
            return False
        return credentials['password_hash'] == self.hash_password(password)