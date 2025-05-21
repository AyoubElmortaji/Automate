import json
import os
from collections import deque, defaultdict
from typing import List, Dict,Set
from classes.Alphabet import Alphabet
from classes.Etat import Etat
from classes.Transition import Transition
from typing import Set, Dict, Tuple, List

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
        # ovir si il ya plus de une etat initiaux
        initial_states = [state for state in self.etats if "initial" in state.type]
        if len(initial_states) != 1:
            return False
        
        transitions = defaultdict(dict)
        for t in self.transitions:
            if t.alphabet.valeur in transitions[t.source.id]:
                return False
            transitions[t.source.id][t.alphabet.valeur] = t.destination.id
        return True
    
    from collections import deque, defaultdict

    def determiniser(self):
        if self.est_deterministe():
            return self  # Already deterministic

        # 1. Initialize with ε-closure of initial states
        initial_states = {e.id for e in self.etats if "initial" in e.type}
        epsilon_closure = self.calculer_epsilon_fermeture(initial_states)
        
        # State management
        new_states = {
            "q" + "_".join(sorted(map(str, epsilon_closure))): {
                "nfa_states": frozenset(epsilon_closure),
                "obj": None  # Will store the Etat object
            }
        }
        queue = deque([frozenset(epsilon_closure)])
        
        # Create DFA
        afd = Automate(nom=f"{self.nom}_AFD")
        
        # First create all states with proper Etat parameters
        for state_name, state_data in new_states.items():
            nfa_states = state_data["nfa_states"]
            is_final = any(e_id in {e.id for e in self.etats if "final" in e.type} 
                        for e_id in nfa_states)
            
            state_type = ("initial" if state_name == "q" + "_".join(sorted(map(str, epsilon_closure)))
                        else "final" if is_final else "normal")
            
            # Create state using EXACT Etat parameters
            etat = Etat(
                id_etat=len(afd.etats) + 1,
                label_etat=state_name,
                type_etat=state_type
            )
            afd.ajouter_etat(etat)
            state_data["obj"] = etat
        
        # Then add transitions with proper Transition parameters
        while queue:
            current_state = queue.popleft()
            current_state_name = "q" + "_".join(sorted(map(str, current_state)))
            src_state = new_states[current_state_name]["obj"]
            
            for symbol in {a.valeur for a in self.alphabets}:
                destinations = set()
                for state_id in current_state:
                    for t in self.transitions:
                        if t.source.id == state_id and t.alphabet.valeur == symbol:
                            destinations.add(t.destination.id)
                
                if destinations:
                    dest_closure = self.calculer_epsilon_fermeture(destinations)
                    dest_name = "q" + "_".join(sorted(map(str, dest_closure)))
                    
                    if dest_name not in new_states:
                        # Create destination state
                        is_final = any(e_id in {e.id for e in self.etats if "final" in e.type} 
                                    for e_id in dest_closure)
                        dest_etat = Etat(
                            id_etat=len(afd.etats) + 1,
                            label_etat=dest_name,
                            type_etat="final" if is_final else "normal"
                        )
                        afd.ajouter_etat(dest_etat)
                        new_states[dest_name] = {
                            "nfa_states": frozenset(dest_closure),
                            "obj": dest_etat
                        }
                        queue.append(frozenset(dest_closure))
                    
                    # Create transition using EXACT Transition parameters
                    alphabet = next(a for a in self.alphabets if a.valeur == symbol)
                    transition = Transition(
                        id_transition=len(afd.transitions) + 1,
                        etat_source=src_state,
                        etat_destination=new_states[dest_name]["obj"],
                        alphabet=alphabet
                    )
                    afd.ajouter_transition(transition)
        
        return afd
    
    def calculer_epsilon_fermeture(self, etats):
        """Compute ε-closure for a set of states"""
        fermeture = set(etats)
        queue = deque(etats)
        
        while queue:
            etat_id = queue.popleft()
            for t in self.transitions:
                if t.source.id == etat_id and t.alphabet.valeur == "ε":
                    if t.destination.id not in fermeture:
                        fermeture.add(t.destination.id)
                        queue.append(t.destination.id)
        return fermeture
    
    def est_complet(self) -> bool:
    # Create a mapping of source state to its outgoing transitions by symbol
        transitions = defaultdict(set)
        for t in self.transitions:
            transitions[t.source.id].add(t.alphabet.valeur)

        # Get all symbols in the alphabet
        alphabet_symbols = {a.valeur for a in self.alphabets}

        # Check for each state and each symbol
        for etat in self.etats:
            state_id = etat.id
            for symbol in alphabet_symbols:
                if symbol not in transitions[state_id]:
                    return False
        return True
    
    def completer_automate(self):
       
        # Check if a sink state ("Puits") already exists
        sink = next((e for e in self.etats if e.label == "Puits"), None)
        if not sink:
            sink_id = max((e.id for e in self.etats), default=0) + 1
            sink = Etat(sink_id, "Puits", "normal")
            self.ajouter_etat(sink)

        symbols = {a.valeur for a in self.alphabets}

        # Add missing transitions to sink
        for etat in self.etats:
            if etat == sink:
                continue
            existing_symbols = {t.alphabet.valeur for t in self.transitions if t.source.id == etat.id}
            for symbol in symbols - existing_symbols:
                alphabet_obj = next(a for a in self.alphabets if a.valeur == symbol)
                transition_id = max((t.id for t in self.transitions), default=0) + 1
                self.ajouter_transition(Transition(transition_id, etat, sink, alphabet_obj))

        # Add self-loops for sink state
        for symbol in symbols:
            if not any(t.source.id == sink.id and t.alphabet.valeur == symbol for t in self.transitions):
                alphabet_obj = next(a for a in self.alphabets if a.valeur == symbol)
                transition_id = max((t.id for t in self.transitions), default=0) + 1
                self.ajouter_transition(Transition(transition_id, sink, sink, alphabet_obj))



    def est_minimal(self) -> bool:
        print("→ Vérification de minimalité...")
        if not self.est_deterministe():
            print("Non déterministe.")
            return False
        if not self.tous_etats_accessibles():
            print("Contient des états inaccessibles.")
            return False
        if not self.tous_etats_distinguables():
            print("Contient des états équivalents.")
            return False
        print("L'automate est minimal.")
        return True

    def tous_etats_accessibles(self) -> bool:
        """Vérifie que tous les états sont accessibles depuis l'état initial"""
        etats_accessibles = set()
        etats_initiaux = [e for e in self.etats if "initial" in e.type]
        
        if not etats_initiaux:
            return False
        
        file = deque([etats_initiaux[0].id])
        etats_accessibles.add(etats_initiaux[0].id)
        
        while file:
            etat_id = file.popleft()
            for transition in self.transitions:
                if transition.source.id == etat_id:
                    if transition.destination.id not in etats_accessibles:
                        etats_accessibles.add(transition.destination.id)
                        file.append(transition.destination.id)
        
        return len(etats_accessibles) == len(self.etats)

    def tous_etats_distinguables(self) -> bool:
        """Implémentation de l'algorithme de Moore pour vérifier la distinguabilité"""
        # Partition initiale : F vs Q\F
        F = {e.id for e in self.etats if "final" in e.type}
        non_F = {e.id for e in self.etats} - F
        partitions = [F, non_F] if non_F else [F]
        
        # Table des transitions
        transition_table = {
            etat.id: {
                a.valeur: next(
                    (t.destination.id for t in self.transitions 
                    if t.source.id == etat.id and t.alphabet.valeur == a.valeur),
                    None
                )
                for a in self.alphabets
            }
            for etat in self.etats
        }
        
        changed = True
        while changed:
            changed = False
            nouvelles_partitions = []
            
            for groupe in partitions:
                sous_groupes = {}
                
                for etat_id in groupe:
                    cle = tuple(
                        next(
                            (i for i, p in enumerate(partitions) 
                            if transition_table[etat_id][a.valeur] in p),
                            -1
                        )
                        for a in self.alphabets
                    )
                    
                    if cle not in sous_groupes:
                        sous_groupes[cle] = []
                    sous_groupes[cle].append(etat_id)
                
                nouvelles_partitions.extend(sous_groupes.values())
                if len(sous_groupes) > 1:
                    changed = True
            
            partitions = nouvelles_partitions
        
        # Si chaque état est dans sa propre partition, ils sont tous distinguables
        return all(len(p) == 1 for p in partitions)
    

    
    
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

    def generer_mots_acceptes(self, max_length) -> Set[str]:
        
        etat_initial = next((etat for etat in self.etats if etat.type == "initial"), None)
        if not etat_initial:
            return set()
        etats_finaux = {etat for etat in self.etats if etat.type == "final"}
        mots_acceptes = set()
        file = deque([(etat_initial, "")]) 

        while file:
            etat_actuel, mot_actuel = file.popleft()
            if len(mot_actuel) > max_length:
                continue
            if etat_actuel in etats_finaux:
                mots_acceptes.add(mot_actuel)
            for trans in self.transitions:
                if trans.source == etat_actuel:
                    nouveau_mot = mot_actuel + trans.alphabet.valeur
                    file.append((trans.destination, nouveau_mot))
        return mots_acceptes  

    def generer_mots_rejetes(self, max_length) -> set:
        etat_initial = next((e for e in self.etats if e.type == "initial"), None)
        etats_finaux = {e for e in self.etats if e.type == "final"}
        if not etat_initial:
            return set()
        mots_rejetes = set()
        file = deque([(etat_initial, "", False)])  
        while file:
            etat, mot, est_rejete = file.popleft()
            if len(mot) > max_length:
                continue
            if len(mot) == max_length and etat not in etats_finaux:
                mots_rejetes.add(mot)
                continue
            nouveau_rejete = est_rejete or (etat not in etats_finaux and len(mot) > 0)
            for trans in self.transitions:
                nouveau_mot = mot + trans.alphabet.valeur
                if nouveau_rejete and len(nouveau_mot) <= max_length:
                    mots_rejetes.add(nouveau_mot)        
                file.append((trans.destination, nouveau_mot, nouveau_rejete))

        return mots_rejetes


    def sont_equivalents(afd1, afd2, max_length) -> tuple[bool, str]:
        alpha1 = {a.valeur for a in afd1.alphabets}
        alpha2 = {a.valeur for a in afd2.alphabets}
        if alpha1 != alpha2:
            return False, "Les alphabets des automates sont différents"
        
        etat_initial1 = next((e for e in afd1.etats if "initial" in e.type), None)
        etat_initial2 = next((e for e in afd2.etats if "initial" in e.type), None)
        if not etat_initial1:
            return False, "Premier automate sans état initial"
        if not etat_initial2:
            return False, "Second automate sans état initial"
        
        file = deque()
        file.append((etat_initial1, etat_initial2, ""))
        visited = set()
        while file:
            e1, e2, mot = file.popleft()
            e1_final = "final" in e1.type
            e2_final = "final" in e2.type
            if e1_final != e2_final:
                return False, f"Différence d'acceptation après le mot '{mot}' (état {e1.id} vs {e2.id})"

            if (e1.id, e2.id) in visited:
                continue
            visited.add((e1.id, e2.id))

            if len(mot) >= max_length:
                continue

            for symbole in alpha1:
                dest1 = next(
                    (t.destination for t in afd1.transitions 
                    if t.source.id == e1.id and t.alphabet.valeur == symbole),
                    None
                )
                dest2 = next(
                    (t.destination for t in afd2.transitions 
                    if t.source.id == e2.id and t.alphabet.valeur == symbole),
                    None
                )            
                if (dest1 is None) != (dest2 is None):
                    return False, (
                        f"Transition manquante pour le symbole '{symbole}' "
                        f"après le mot '{mot}'\n"
                        f"- Automate 1: {'présente' if dest1 else 'absente'}\n"
                        f"- Automate 2: {'présente' if dest2 else 'absente'}"
                    )

                if dest1 and dest2:
                    file.append((dest1, dest2, mot + symbole))
        return True, f"Les automates sont équivalents pour tous les mots de longueur ≤ {max_length}"  

    def union_mots(self, autre_automate: 'Automate', max_length: int = 5) -> set:
        if {a.valeur for a in self.alphabets} != {a.valeur for a in autre_automate.alphabets}:
            raise ValueError("Les alphabets doivent être identiques")
        mots_self = self.generer_mots_acceptes(max_length)
        mots_autre = autre_automate.generer_mots_acceptes(max_length)      
        return mots_self.union(mots_autre)


    
    def intersection_mots(self, autre_automate: 'Automate', max_length: int = 5) -> set:
        if {a.valeur for a in self.alphabets} != {a.valeur for a in autre_automate.alphabets}:
            raise ValueError("Les alphabets doivent être identiques")
        return (
            self.generer_mots_acceptes(max_length) & 
            autre_automate.generer_mots_acceptes(max_length)
        )
    
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