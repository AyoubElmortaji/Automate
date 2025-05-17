class Alphabet:
    def __init__(self, id_alphabet: int, val_alphabet: str):
        self.id = id_alphabet
        self.valeur = val_alphabet
    
    def __str__(self):
        return f"Alphabet(id={self.id}, valeur='{self.valeur}')"
    
    def to_dict(self):
        return {"idAlphabet": self.id, "valAlphabet": self.valeur}
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["idAlphabet"], data["valAlphabet"])