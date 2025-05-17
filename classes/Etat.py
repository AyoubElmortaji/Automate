class Etat:
    def __init__(self, id_etat: int, label_etat: str, type_etat: str = "normal"):
        self.id = id_etat
        self.label = label_etat
        self.type = type_etat.lower()
    
    def __str__(self):
        return f"Etat(id={self.id}, label='{self.label}', type='{self.type}')"
    
    def to_dict(self):
        return {"idEtat": self.id, "labelEtat": self.label, "typeEtat": self.type}
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["idEtat"], data["labelEtat"], data["typeEtat"])