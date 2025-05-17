from classes.Etat import Etat
from classes.Alphabet import Alphabet

class Transition:
    def __init__(self, id_transition: int, etat_source: Etat, etat_destination: Etat, alphabet: Alphabet):
        self.id = id_transition
        self.source = etat_source
        self.destination = etat_destination
        self.alphabet = alphabet
    
    def __str__(self):
        return f"{self.source.label} --{self.alphabet.valeur}--> {self.destination.label}"
    
    def to_dict(self):
        return {
            "idTransition": self.id,
            "etatSource": self.source.id,
            "etatDestination": self.destination.id,
            "alphabet": self.alphabet.id
        }
    
    @classmethod
    def from_dict(cls, data: dict, etats_dict: dict, alphabets_dict: dict):
        return cls(
            data["idTransition"],
            etats_dict[data["etatSource"]],
            etats_dict[data["etatDestination"]],
            alphabets_dict[data["alphabet"]]
        )