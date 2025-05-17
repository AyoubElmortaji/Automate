import json
import os
from collections import defaultdict
from typing import List, Dict
from classes.Alphabet import Alphabet
from classes.Etat import Etat
from classes.Transition import Transition

class Automate:
    def __init__(self, nom: str):
        self.nom = nom
        self.alphabets: List[Alphabet] = []
        self.etats: List[Etat] = []
        self.transitions: List[Transition] = []
    
    def ajouter_alphabet(self, alphabet: Alphabet):
        if any(a.valeur == alphabet.valeur for a in self.alphabets):
            raise ValueError(f"Symbole '{alphabet.valeur}' existe déjà")
        self.alphabets.append(alphabet)
    
    def ajouter_etat(self, etat: Etat):
        if any(e.id == etat.id for e in self.etats):
            raise ValueError(f"État avec ID {etat.id} existe déjà")
        self.etats.append(etat)
    
    def ajouter_transition(self, transition: Transition):
        self.transitions.append(transition)
    
    def est_deterministe(self) -> bool:
        transitions = defaultdict(dict)
        for t in self.transitions:
            if t.alphabet.valeur in transitions[t.source.id]:
                return False
            transitions[t.source.id][t.alphabet.valeur] = t.destination.id
        return True
    
    def reconnait_mot(self, mot: str) -> bool:
        etats_actuels = {e.id for e in self.etats if "initial" in e.type}
        
        for symbole in mot:
            nouveaux_etats = set()
            for etat_id in etats_actuels:
                for t in self.transitions:
                    if t.source.id == etat_id and t.alphabet.valeur == symbole:
                        nouveaux_etats.add(t.destination.id)
            if not nouveaux_etats:
                return False
            etats_actuels = nouveaux_etats
        
        return any("final" in e.type for e in self.etats if e.id in etats_actuels)
    
    def sauvegarder(self):
        os.makedirs("automates", exist_ok=True)
        with open(f"automates/{self.nom}.json", "w") as f:
            json.dump({
                "nom": self.nom,
                "alphabets": [a.to_dict() for a in self.alphabets],
                "etats": [e.to_dict() for e in self.etats],
                "transitions": [t.to_dict() for t in self.transitions]
            }, f, indent=4)
    
    @classmethod
    def charger(cls, nom: str):
        with open(f"automates/{nom}.json", "r") as f:
            data = json.load(f)
        
        automate = cls(data["nom"])
        
        # Chargement des alphabets
        alphabets = {a["idAlphabet"]: Alphabet.from_dict(a) for a in data["alphabets"]}
        for a in alphabets.values():
            automate.ajouter_alphabet(a)
        
        # Chargement des états
        etats = {e["idEtat"]: Etat.from_dict(e) for e in data["etats"]}
        for e in etats.values():
            automate.ajouter_etat(e)
        
        # Chargement des transitions
        for t in data["transitions"]:
            automate.ajouter_transition(Transition.from_dict(t, etats, alphabets))
        
        return automate
    
    def __str__(self):
        return (
            f"Automate {self.nom}\n"
            f"Alphabet: {[a.valeur for a in self.alphabets]}\n"
            f"États: {[f'{e.label}({e.type})' for e in self.etats]}\n"
            f"Transitions: {[str(t) for t in self.transitions]}"
        )