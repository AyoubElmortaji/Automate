import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Menu
import json
import os
import random
import math
from pathlib import Path
from typing import Optional
from datetime import datetime

from classes.security import SecurityManager
from classes.Alphabet import Alphabet
from classes.Etat import Etat
from classes.Transition import Transition
from classes.Automate import Automate


class ModernAutomateApp:
    """Application principale pour gérer les automates avec une interface graphique."""

    def __init__(self, root):
        """On initialise l'appli avec la fenêtre principale et les configs de base."""
        self.root = root
        self.root.title("Automata - ENSAM CASA")
        self.automate_courant: Optional[Automate] = None
        self.security = SecurityManager()
        self.colors = {
            "primary": "#4a6fa5",
            "secondary": "#f8f9fa",
            "accent": "#007bff",
            "text": "#212529",
            "border": "#ced4da",
            "canvas_bg": "#ffffff",
            "final_state_bg": "#d4edda"
        }
        
        self.setup_styles()
        self.setup_ui()
        self.create_menubar()
        self.actualiser_liste()
        self.center_window()

    def center_window(self):
        """Centre la fenêtre principale au milieu de l'écran."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def setup_styles(self):
        """Définit les styles visuels pour l'interface (couleurs, polices, etc.)."""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('.', background=self.colors["secondary"], foreground=self.colors["text"], font=('Segoe UI', 10))
        style.configure('TFrame', background=self.colors["secondary"])
        style.configure('TLabel', background=self.colors["secondary"], foreground=self.colors["text"])
        style.configure('TButton',
                       background=self.colors["accent"],
                       foreground='white',
                       font=('Segoe UI', 9, 'bold'),
                       borderwidth=0,
                       padding=[10, 5],
                       relief="flat")
        style.map('TButton',
                 background=[('active', '#0056b3')],
                 foreground=[('active', 'white')])
        style.configure('TNotebook', background=self.colors["secondary"], borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.colors["secondary"],
                       foreground=self.colors["text"],
                       padding=[15, 8],
                       font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors["primary"])],
                 foreground=[('selected', 'white')])
        style.configure('TScrollbar', troughcolor=self.colors["secondary"], bordercolor=self.colors["border"], arrowcolor=self.colors["text"])
        self.root.configure(bg=self.colors["secondary"])

    def setup_ui(self):
        """Met en place toute l'interface graphique (panneaux, onglets, boutons, etc.)."""
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)

        # Panneau principal avec séparation horizontale
        main_pane = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sidebar à gauche pour la liste des automates
        left_frame = ttk.Frame(main_pane, width=300, style='TFrame')
        main_pane.add(left_frame, weight=1)

        # Ajout du logo et du nom de l'application
        try:
            logo_path = Path("./logoEnsam.png")
            if logo_path.exists():
                self.logo_image = tk.PhotoImage(file=logo_path)
                # Redimensionner l'image si nécessaire (par exemple, 100x100 pixels)
                self.logo_image = self.logo_image.subsample(2, 2)  # Ajuste selon la taille réelle de l'image
                logo_label = ttk.Label(left_frame, image=self.logo_image, background=self.colors["secondary"])
                logo_label.pack(pady=(10, 5))
            else:
                # Placeholder si le logo n'existe pas
                logo_label = ttk.Label(left_frame, text="[Logo Placeholder]", font=('Segoe UI', 10, 'italic'), background=self.colors["secondary"])
                logo_label.pack(pady=(10, 5))
        except tk.TclError as e:
            # En cas d'erreur de chargement de l'image
            logo_label = ttk.Label(left_frame, text="[Erreur Logo]", font=('Segoe UI', 10, 'italic'), background=self.colors["secondary"])
            logo_label.pack(pady=(10, 5))

        # Nom de l'application
        ttk.Label(left_frame, text="Automata - ENSAM CASA", font=('Segoe UI', 12, 'bold'), background=self.colors["secondary"]).pack(pady=(0, 10))

        # Liste des automates sauvegardés
        ttk.Label(left_frame, text="Automates Sauvegardés", font=('Segoe UI', 11, 'bold')).pack(pady=(0, 5), padx=10, anchor='w')

        list_container = ttk.Frame(left_frame, style='TFrame')
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(list_container, style='TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.liste_automates = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=('Segoe UI', 10),
            bg=self.colors["canvas_bg"],
            fg=self.colors["text"],
            selectbackground=self.colors["accent"],
            selectforeground='white',
            bd=1,
            relief="solid",
            highlightthickness=0
        )
        self.liste_automates.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.liste_automates.yview)
        self.liste_automates.bind('<<ListboxSelect>>', self.charger_automate)

        # Boutons pour actualiser et supprimer
        btn_frame = ttk.Frame(left_frame, style='TFrame')
        btn_frame.pack(fill=tk.X, pady=5, padx=10)

        ttk.Button(btn_frame, text="Actualiser", command=self.actualiser_liste, style='TButton').pack(side=tk.LEFT, expand=True, padx=(0, 5))
        ttk.Button(btn_frame, text="Supprimer", command=self.supprimer_automate, style='TButton').pack(side=tk.LEFT, expand=True, padx=(5, 0))

        ttk.Frame(left_frame, height=10, style='TFrame').pack()

        # Zone principale à droite
        right_frame = ttk.Frame(main_pane, style='TFrame')
        main_pane.add(right_frame, weight=3)

        notebook = ttk.Notebook(right_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet Détails
        details_frame = ttk.Frame(notebook, style='TFrame')
        notebook.add(details_frame, text="Détails")

        text_container = ttk.Frame(details_frame, style='TFrame')
        text_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        yscroll_details = ttk.Scrollbar(text_container, style='TScrollbar')
        yscroll_details.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_details = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.colors["canvas_bg"],
            fg=self.colors["text"],
            yscrollcommand=yscroll_details.set,
            bd=1,
            relief="solid"
        )
        self.text_details.pack(fill=tk.BOTH, expand=True)
        yscroll_details.config(command=self.text_details.yview)

        # Onglet Visualisation
        visu_frame = ttk.Frame(notebook, style='TFrame')
        notebook.add(visu_frame, text="Visualisation")

        self.canvas = tk.Canvas(visu_frame, bg=self.colors["canvas_bg"], bd=1, relief="solid")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Barre d'outils en bas
        tool_frame = ttk.Frame(self.root, style='TFrame')
        tool_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Label(tool_frame, text="Actions Rapides:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 10))

        actions = [
            ("Ajouter Symbole", self.ajouter_symbole),
            ("Ajouter État", self.ajouter_etat),
            ("Ajouter Transition", self.ajouter_transition),
        ]

        for text, cmd in actions:
            ttk.Button(tool_frame, text=text, command=cmd, style='TButton').pack(side=tk.LEFT, padx=5)

    def create_menubar(self):
        """Crée la barre de menus avec toutes les options."""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # Menu Automates
        automate_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Automates", menu=automate_menu)
        automate_menu.add_command(label="Créer un nouvel automate", command=self.creer_automate)
        automate_menu.add_command(label="Ouvrir et charger un automate...", command=self.charger_automate_menu)
        automate_menu.add_command(label="Sauvegarder l'automate actuel", command=self.sauvegarder_automate)
        automate_menu.add_command(label="Modifier l'automate actuel", command=self.modifier_automate)
        automate_menu.add_separator()
        automate_menu.add_command(label="Quitter", command=self.root.quit)

        # Menu Analyse
        analyse_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Analyse", menu=analyse_menu)
        analyse_menu.add_command(label="Vérifier si un automate est déterministe", command=self.verifier_determinisme)
        analyse_menu.add_command(label="Transformer un AFN en AFD", command=self.transformer_afn_afd)
        analyse_menu.add_command(label="Vérifier si un automate est complet", command=self.verifier_complet)
        analyse_menu.add_command(label="Compléter un automate", command=self.completer_automate)
        analyse_menu.add_command(label="Vérifier si un automate est minimal", command=self.verifier_minimal)
        analyse_menu.add_command(label="Minimiser un automate", command=self.minimiser_automate)

        # Menu Avancée
        avancee_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Avancée", menu=avancee_menu)
        avancee_menu.add_command(label="Tester si un mot est reconnu", command=self.tester_mot)
        avancee_menu.add_command(label="Générer mots acceptés (longueur max)", command=self.generer_mots_acceptes)
        avancee_menu.add_command(label="Tester l'équivalence entre deux automates", command=self.tester_equivalence)
        avancee_menu.add_command(label="Calculer Union de deux automates", command=self.calculerunion)
        avancee_menu.add_command(label="Calculer Intersection de deux automates", command=self.calculer_intersection)
        avancee_menu.add_command(label="Calculer Complément d'un automate", command=self.calculer_complement)
        avancee_menu.add_command(label="Afficher mots rejetés (longueur max)", command=self.afficher_mots_rejetes)

        # Menu Sécurité
        security_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Sécurité", menu=security_menu)
        security_menu.add_command(label="Afficher les informations de sécurité", command=self.afficher_infos_securite)
        security_menu.add_command(label="Changer le mot de passe", command=self.changer_mot_de_passe)

    def on_canvas_resize(self, event=None):
        """Redessine l'automate quand le canvas change de taille."""
        self.dessiner_automate()

    def dessiner_automate(self):
        """Dessine l'automate actuel sur le canvas (états, transitions, etc.)."""
        self.canvas.delete("all")
        if not self.automate_courant:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        center_x, center_y = canvas_width // 2, canvas_height // 2
        num_etats = len(self.automate_courant.etats)
        state_radius = 30
        layout_radius = min(center_x, center_y) * 0.7

        if num_etats == 0:
            return

        etat_pos = {}
        transitions_grouped = {}
        for t in self.automate_courant.transitions:
            key = (t.source.id, t.destination.id)
            if key not in transitions_grouped:
                transitions_grouped[key] = []
            transitions_grouped[key].append(t.alphabet.valeur)

        for i, etat in enumerate(self.automate_courant.etats):
            angle = (2 * math.pi / num_etats) * i if num_etats > 1 else 0
            x = center_x + layout_radius * math.cos(angle)
            y = center_y + layout_radius * math.sin(angle)
            etat_pos[etat.id] = (x, y)

            outline_color = self.colors["primary"] if "initial" in etat.type else self.colors["text"]
            fill_color = self.colors["secondary"] if "final" not in etat.type else self.colors["final_state_bg"]
            self.canvas.create_oval(x - state_radius, y - state_radius, x + state_radius, y + state_radius,
                                   outline=outline_color, fill=fill_color, width=2)
            self.canvas.create_text(x, y, text=etat.label, font=('Arial', 10, 'bold'), fill=self.colors["text"])

            if "initial" in etat.type:
                arrow_length = 20
                arrow_end_x = x - state_radius * math.cos(angle)
                arrow_end_y = y - state_radius * math.sin(angle)
                arrow_start_x = x - (state_radius + arrow_length) * math.cos(angle)
                arrow_start_y = y - (state_radius + arrow_length) * math.sin(angle)
                self.canvas.create_line(arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                       arrow=tk.LAST, width=2, fill=self.colors["primary"])

            if "final" in etat.type:
                inner_radius = state_radius - 5
                self.canvas.create_oval(x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius,
                                       outline=self.colors["text"], width=2)

        for (src_id, dest_id), symbols in transitions_grouped.items():
            src_x, src_y = etat_pos[src_id]
            dest_x, dest_y = etat_pos[dest_id]
            label = ', '.join(symbols)

            if src_id == dest_id:
                loop_radius = state_radius * 0.8
                loop_center_x = src_x + state_radius * 0.8
                loop_center_y = src_y - state_radius * 0.8
                bbox = (loop_center_x - loop_radius, loop_center_y - loop_radius,
                        loop_center_x + loop_radius, loop_center_y + loop_radius)
                self.canvas.create_arc(bbox, start=225, extent=270, style=tk.ARC, outline=self.colors["text"], width=2)

                arrow_angle = math.radians(225 + 270 - 10)
                arrow_x = loop_center_x + loop_radius * math.cos(arrow_angle)
                arrow_y = loop_center_y - loop_radius * math.sin(arrow_angle)
                self.canvas.create_line(arrow_x, arrow_y, arrow_x - 5, arrow_y + 5, arrow=tk.LAST, width=2, fill=self.colors["text"])
                self.canvas.create_text(loop_center_x, loop_center_y - loop_radius - 5,
                                       text=label, font=('Arial', 9), fill=self.colors["text"])
            else:
                angle = math.atan2(dest_y - src_y, dest_x - src_x)
                arrow_start_x = src_x + state_radius * math.cos(angle)
                arrow_start_y = src_y + state_radius * math.sin(angle)
                arrow_end_x = dest_x - state_radius * math.cos(angle)
                arrow_end_y = dest_y - state_radius * math.sin(angle)
                self.canvas.create_line(arrow_start_x, arrow_start_y, arrow_end_x, arrow_end_y,
                                       arrow=tk.LAST, width=2, fill=self.colors["text"])
                mid_x, mid_y = (arrow_start_x + arrow_end_x) / 2, (arrow_start_y + arrow_end_y) / 2
                label_offset = 15
                text_x = mid_x + label_offset * math.sin(angle)
                text_y = mid_y - label_offset * math.cos(angle)
                self.canvas.create_text(text_x, text_y, text=label, font=('Arial', 9, 'bold'), fill=self.colors["primary"])

    def actualiser_liste(self):
        """Met à jour la liste des automates sauvegardés dans le dossier 'automates'."""
        self.liste_automates.delete(0, tk.END)
        Path("automates").mkdir(exist_ok=True)
        for f in Path("automates").glob("*.json"):
            self.liste_automates.insert(tk.END, f.stem)

    def creer_automate(self):
        """Crée un nouvel automate avec un nom et un mot de passe."""
        nom = simpledialog.askstring("Nouvel Automate", "Nom de l'automate:", parent=self.root)
        if nom:
            if Path(f"automates/{nom}.json").exists():
                messagebox.showerror("Erreur", f"Un automate nommé '{nom}' existe déjà.", parent=self.root)
                return

            password = simpledialog.askstring("Sécurité", "Définir un mot de passe pour cet automate:", 
                                           parent=self.root, show='*')
            if not password:
                return

            self.automate_courant = Automate(nom)
            self.security.save_credentials(nom, password)
            messagebox.showinfo("Succès", f"Automate '{nom}' créé. Ajoutez d'abord des symboles et des états.", parent=self.root)
            self.afficher_details()
            self.dessiner_automate()

    def charger_automate(self, event):
        """Charge un automate depuis la liste en vérifiant le mot de passe."""
        selection = self.liste_automates.curselection()
        if selection:
            nom = self.liste_automates.get(selection[0])
            try:
                password = simpledialog.askstring("Authentification", 
                                               f"Entrez le mot de passe pour '{nom}':", 
                                               parent=self.root, show='*')
                if not password:
                    return
                
                if not self.security.verify_password(nom, password):
                    messagebox.showerror("Erreur", "Mot de passe incorrect", parent=self.root)
                    return
                
                self.automate_courant = Automate.charger(nom)
                messagebox.showinfo("Automate Chargé", f"Automate '{nom}' chargé avec succès.", parent=self.root)
                self.afficher_details()
                self.dessiner_automate()
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Automate '{nom}' non trouvé.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de chargement: {str(e)}", parent=self.root)

    def charger_automate_menu(self):
        """Charge un automate via le menu en demandant son nom et mot de passe."""
        nom = simpledialog.askstring("Ouvrir Automate", "Nom de l'automate à charger:", parent=self.root)
        if nom:
            try:
                password = simpledialog.askstring("Authentification", 
                                               f"Entrez le mot de passe pour '{nom}':", 
                                               parent=self.root, show='*')
                if not password:
                    return
                
                if not self.security.verify_password(nom, password):
                    messagebox.showerror("Erreur", "Mot de passe incorrect", parent=self.root)
                    return
                
                self.automate_courant = Automate.charger(nom)
                messagebox.showinfo("Automate Chargé", f"Automate '{nom}' chargé avec succès.", parent=self.root)
                self.afficher_details()
                self.dessiner_automate()
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Automate '{nom}' non trouvé.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur de chargement: {str(e)}", parent=self.root)

    def sauvegarder_automate(self):
        """Sauvegarde l'automate actuel après vérification du mot de passe."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate à sauvegarder", parent=self.root)
            return
        
        password = simpledialog.askstring("Authentification", 
                                       f"Entrez le mot de passe pour '{self.automate_courant.nom}':", 
                                       parent=self.root, show='*')
        if not password:
            return
        
        if not self.security.verify_password(self.automate_courant.nom, password):
            messagebox.showerror("Erreur", "Mot de passe incorrect", parent=self.root)
            return

        if not self.automate_courant.etats:
            messagebox.showwarning("Attention", "L'automate ne contient aucun état et ne sera pas sauvegardé.", parent=self.root)
            return
        
        try:
            self.automate_courant.sauvegarder()
            self.security.save_credentials(self.automate_courant.nom, password)
            messagebox.showinfo("Succès", "Automate sauvegardé avec succès", parent=self.root)
            self.actualiser_liste()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de sauvegarde: {str(e)}", parent=self.root)

    def supprimer_automate(self):
        """Supprime un automate sélectionné après confirmation."""
        selection = self.liste_automates.curselection()
        if not selection:
            messagebox.showinfo("Information", "Veuillez sélectionner un automate à supprimer.", parent=self.root)
            return

        nom = self.liste_automates.get(selection[0])
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer l'automate '{nom}' ?", parent=self.root):
            try:
                os.remove(f"automates/{nom}.json")
                if self.automate_courant and self.automate_courant.nom == nom:
                    self.automate_courant = None
                    self.text_details.config(state=tk.NORMAL)
                    self.text_details.delete(1.0, tk.END)
                    self.text_details.config(state=tk.DISABLED)
                    self.canvas.delete("all")
                self.actualiser_liste()
                messagebox.showinfo("Succès", f"Automate '{nom}' supprimé.", parent=self.root)
            except FileNotFoundError:
                messagebox.showerror("Erreur", f"Automate '{nom}' non trouvé.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de suppression: {str(e)}", parent=self.root)

    def ajouter_symbole(self):
        """Ajoute un symbole à l'alphabet de l'automate actuel."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné", parent=self.root)
            return

        symbole = simpledialog.askstring("Ajouter Symbole", "Symbole (1 caractère):", parent=self.root)
        if symbole is not None:
            if len(symbole) == 1:
                try:
                    max_id = max([a.id for a in self.automate_courant.alphabets], default=0)
                    new_id = max_id + 1
                    self.automate_courant.ajouter_alphabet(Alphabet(new_id, symbole))
                    self.afficher_details()
                except ValueError as e:
                    messagebox.showerror("Erreur", str(e), parent=self.root)
            else:
                messagebox.showerror("Erreur", "Le symbole doit être un seul caractère.", parent=self.root)

    def ajouter_etat(self):
        """Ajoute un nouvel état à l'automate actuel."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné", parent=self.root)
            return

        label = simpledialog.askstring("Ajouter État", "Nom de l'état:", parent=self.root)
        if label is not None:
            if any(e.label == label for e in self.automate_courant.etats):
                messagebox.showerror("Erreur", f"Un état avec le nom '{label}' existe déjà.", parent=self.root)
                return

            type_etat = simpledialog.askstring(
                "Type d'état",
                "Type (initial/final/normal):",
                initialvalue="normal", parent=self.root
            )
            if type_etat is not None:
                if type_etat.lower() in ["initial", "final", "normal"]:
                    try:
                        max_id = max([e.id for e in self.automate_courant.etats], default=0)
                        new_id = max_id + 1
                        self.automate_courant.ajouter_etat(Etat(new_id, label, type_etat))
                        self.afficher_details()
                        self.dessiner_automate()
                    except ValueError as e:
                        messagebox.showerror("Erreur", str(e), parent=self.root)
                else:
                    messagebox.showerror("Erreur", "Type d'état invalide. Utilisez 'initial', 'final', ou 'normal'.", parent=self.root)

    def ajouter_transition(self):
        """Ajoute une transition à l'automate actuel via une fenêtre de dialogue."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return

        if not self.automate_courant.etats:
            messagebox.showerror("Erreur", "Aucun état n'est défini dans l'automate.", parent=self.root)
            return

        if not self.automate_courant.alphabets:
            messagebox.showerror("Erreur", "Aucun symbole défini dans l'alphabet.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter Transition")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors["secondary"])

        dialog_frame = ttk.Frame(dialog, padding="10", style='TFrame')
        dialog_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(dialog_frame, text="État source:", style='TLabel').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        src_var = tk.StringVar()
        src_cb = ttk.Combobox(dialog_frame, textvariable=src_var, state="readonly")
        src_cb["values"] = [f"{e.id}: {e.label}" for e in self.automate_courant.etats]
        if self.automate_courant.etats:
            src_cb.set(src_cb["values"][0])
        src_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(dialog_frame, text="État destination:", style='TLabel').grid(row=1, column=0, padx=5, pady=5, sticky="w")
        dest_var = tk.StringVar()
        dest_cb = ttk.Combobox(dialog_frame, textvariable=dest_var, state="readonly")
        dest_cb["values"] = [f"{e.id}: {e.label}" for e in self.automate_courant.etats]
        if self.automate_courant.etats:
            dest_cb.set(dest_cb["values"][0])
        dest_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(dialog_frame, text="Symbole:", style='TLabel').grid(row=2, column=0, padx=5, pady=5, sticky="w")
        symbole_var = tk.StringVar()
        symbole_cb = ttk.Combobox(dialog_frame, textvariable=symbole_var, state="readonly")
        symbole_cb["values"] = [a.valeur for a in self.automate_courant.alphabets]
        if self.automate_courant.alphabets:
            symbole_cb.set(symbole_cb["values"][0])
        symbole_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        dialog_frame.columnconfigure(1, weight=1)

        def valider():
            try:
                src_selection = src_var.get()
                dest_selection = dest_var.get()
                symbole = symbole_var.get()

                if not src_selection or not dest_selection or not symbole:
                    messagebox.showerror("Erreur", "Veuillez sélectionner une source, une destination et un symbole.", parent=dialog)
                    return

                src_id = int(src_selection.split(":")[0])
                dest_id = int(dest_selection.split(":")[0])

                etat_src = next(e for e in self.automate_courant.etats if e.id == src_id)
                etat_dest = next(e for e in self.automate_courant.etats if e.id == dest_id)
                alphabet = next(a for a in self.automate_courant.alphabets if a.valeur == symbole)

                max_id = max([t.id for t in self.automate_courant.transitions], default=0)
                new_id = max_id + 1
                self.automate_courant.ajouter_transition(Transition(new_id, etat_src, etat_dest, alphabet))

                self.afficher_details()
                self.dessiner_automate()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erreur", "Sélection d'état invalide.", parent=dialog)
            except StopIteration:
                messagebox.showerror("Erreur", "État source, destination ou symbole introuvable.", parent=dialog)
            except Exception as e:
                messagebox.showerror("Erreur", f"Transition invalide: {str(e)}", parent=dialog)

        ttk.Button(dialog_frame, text="Valider", command=valider, style='TButton').grid(row=3, columnspan=2, pady=10)
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        self.root.wait_window(dialog)

    def modifier_automate(self):
        """Modifie l'automate actuel (pas encore implémenté)."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné à modifier.", parent=self.root)
            return
        messagebox.showinfo("Modifier Automate", "Fonctionnalité de modification à implémenter.", parent=self.root)

    def afficher_details(self):
        """Affiche les détails de l'automate actuel dans l'onglet Détails."""
        self.text_details.config(state=tk.NORMAL)
        self.text_details.delete(1.0, tk.END)

        if self.automate_courant:
            details = [
                f"=== Automate: {self.automate_courant.nom} ===",
                "\nAlphabet: " + ", ".join(a.valeur for a in self.automate_courant.alphabets),
                "\nÉtats:",
                *[f"- {e.label} (ID: {e.id}, Type: {e.type})" for e in self.automate_courant.etats],
                "\nTransitions:",
                *[f"- ID: {t.id}, Source: {t.source.label}, Destination: {t.destination.label}, Symbole: {t.alphabet.valeur}"
                  for t in self.automate_courant.transitions]
            ]
            self.text_details.insert(tk.END, "\n".join(details))
        self.text_details.config(state=tk.DISABLED)

    def tester_mot(self):
        """Teste si un mot est reconnu par l'automate actuel."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné", parent=self.root)
            return
        if not self.automate_courant.etats:
            messagebox.showerror("Erreur", "L'automate ne contient aucun état.", parent=self.root)
            return
        if not any("initial" in e.type for e in self.automate_courant.etats):
            messagebox.showerror("Erreur", "L'automate n'a pas d'état initial.", parent=self.root)
            return
        if not any("final" in e.type for e in self.automate_courant.etats):
            messagebox.showerror("Erreur", "L'automate n'a pas d'état final.", parent=self.root)
            return
        if not self.automate_courant.transitions and len(self.automate_courant.etats) > 1:
            messagebox.showwarning("Attention", "L'automate n'a pas de transitions.", parent=self.root)

        mot = simpledialog.askstring("Tester un mot", "Entrez le mot à tester:", parent=self.root)
        if mot is not None:
            try:
                if self.automate_courant.reconnait_mot(mot):
                    messagebox.showinfo("Résultat", f"Le mot '{mot}' est accepté", parent=self.root)
                else:
                    messagebox.showinfo("Résultat", f"Le mot '{mot}' est rejeté", parent=self.root)
            except Exception as e:
                messagebox.showerror("Erreur", str(e), parent=self.root)

    def verifier_determinisme(self):
        """Vérifie si l'automate actuel est déterministe."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        if self.automate_courant.est_deterministe():
            messagebox.showinfo("Résultat", "L'automate est déterministe.", parent=self.root)
        else:
            messagebox.showinfo("Résultat", "L'automate n'est pas déterministe.", parent=self.root)

    def transformer_afn_afd(self):
        """Transforme un automate non déterministe en déterministe."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        if self.automate_courant.est_deterministe():
            messagebox.showinfo("Résultat", "L'automate est déjà déterministe.", parent=self.root)
            return
        try:
            afd = self.automate_courant.determiniser()
            self.automate_courant = afd
            messagebox.showinfo("Succès", "Transformation AFN → AFD réussie.", parent=self.root)
            self.afficher_details()
            self.dessiner_automate()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la transformation : {str(e)}", parent=self.root)

    def verifier_complet(self):
        """Vérifie si l'automate actuel est complet."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        if self.automate_courant.est_complet():
            messagebox.showinfo("Résultat", "L'automate est complet.", parent=self.root)
        else:
            messagebox.showinfo("Résultat", "L'automate n'est pas complet.", parent=self.root)

    def completer_automate(self):
        """Complète l'automate actuel si nécessaire."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        if self.automate_courant.est_complet():
            messagebox.showinfo("Info", "L'automate est déjà complet.", parent=self.root)
            return
        try:
            self.automate_courant.completer_automate()
            messagebox.showinfo("Succès", "L'automate a été complété avec succès.", parent=self.root)
            self.afficher_details()
            self.dessiner_automate()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la complétion: {str(e)}", parent=self.root)

    def verifier_minimal(self):
        """Vérifie si l'automate actuel est minimal."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        try:
            if self.automate_courant.est_minimal():
                messagebox.showinfo("Résultat", "L'automate est minimal.", parent=self.root)
            else:
                messagebox.showinfo("Résultat", "L'automate n'est pas minimal.", parent=self.root)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la vérification : {str(e)}", parent=self.root)

    def minimiser_automate(self):
        """Minimise l'automate actuel (pas encore implémenté)."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        if self.automate_courant.est_minimal():
            messagebox.showinfo("Résultat", "L'automate est déjà minimal.", parent=self.root)
            return
        messagebox.showinfo("Résultat", "Fonctionnalité de minimisation non implémentée.", parent=self.root)

    def generer_mots_acceptes(self):
        """Génère les mots acceptés par l'automate jusqu'à une longueur donnée."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        nb = simpledialog.askinteger(
            "Longueur maximale",
            "Entrez la longueur (1-10):",
            parent=self.root,
            minvalue=1,
            maxvalue=10
        )
        if nb is None:
            return
        try:
            mots = self.automate_courant.generer_mots_acceptes(max_length=nb)
            messagebox.showinfo("Résultat", f"Mots acceptés générés:\n{', '.join(mots)}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération: {str(e)}", parent=self.root)

    def afficher_mots_rejetes(self):
        """Génère les mots rejetés par l'automate jusqu'à une longueur donnée."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        nb = simpledialog.askinteger(
            "Longueur maximale",
            "Entrez la longueur (1-10):",
            parent=self.root,
            minvalue=1,
            maxvalue=10
        )
        if nb is None:
            return
        try:
            mots = self.automate_courant.generer_mots_rejetes(max_length=nb)
            messagebox.showinfo("Résultat", f"Mots rejetés générés:\n{', '.join(mots)}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération: {str(e)}", parent=self.root)

    def tester_equivalence(self):
        """Teste si deux automates sont équivalents."""
        top = tk.Toplevel(self.root)
        top.title("Test d'équivalence")
        top.geometry("400x300")
        ttk.Label(top, text="Automate 1:").grid(row=0, column=0, padx=5, pady=5)
        combo1 = ttk.Combobox(top, state="readonly")
        combo1.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(top, text="Automate 2:").grid(row=1, column=0, padx=5, pady=5)
        combo2 = ttk.Combobox(top, state="readonly")
        combo2.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(top, text="Longueur max:").grid(row=2, column=0, padx=5, pady=5)
        spin_length = ttk.Spinbox(top, from_=1, to=10, width=5)
        spin_length.set(5)
        spin_length.grid(row=2, column=1, padx=5, pady=5)

        fichiers = sorted(Path("automates").glob("*.json"))
        noms = [f.stem for f in fichiers]
        combo1['values'] = noms
        combo2['values'] = noms
        if len(noms) >= 2:
            combo1.current(0)
            combo2.current(1)

        def lancer_test():
            try:
                auto1 = Automate.charger(combo1.get())
                auto2 = Automate.charger(combo2.get())
                max_len = int(spin_length.get())
                resultat = Automate.sont_equivalents(auto1, auto2, max_len)
                if isinstance(resultat, tuple) and len(resultat) == 2:
                    equivalent, message = resultat
                else:
                    raise ValueError("La fonction doit retourner un tuple (bool, str)")
                if equivalent:
                    messagebox.showinfo("Résultat", message, parent=top)
                else:
                    messagebox.showwarning("Résultat", message, parent=top)
            except Exception as e:
                messagebox.showerror("Erreur", str(e), parent=top)
        
        ttk.Button(top, text="Tester", command=lancer_test).grid(row=3, columnspan=2, pady=10)

    def calculerunion(self):
        """Calcule l'union des mots acceptés par deux automates."""
        fichiers = list(Path("automates").glob("*.json"))
        noms = [f.stem for f in fichiers]
        if len(noms) < 2:
            messagebox.showerror("Erreur", "Besoin d'au moins 2 automates", parent=self.root)
            return
        top = tk.Toplevel(self.root)
        top.title("Union d'automates")
        top.geometry("400x200")
        
        ttk.Label(top, text="Automate 1:").grid(row=0, column=0, padx=5, pady=5)
        combo1 = ttk.Combobox(top, values=noms, state="readonly")
        combo1.current(0)
        combo1.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Automate 2:").grid(row=1, column=0, padx=5, pady=5)
        combo2 = ttk.Combobox(top, values=noms, state="readonly")
        combo2.current(1 if len(noms) > 1 else 0)
        combo2.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Longueur max:").grid(row=2, column=0, padx=5, pady=5)
        spin_length = ttk.Spinbox(top, from_=1, to=20, width=5)
        spin_length.set(5)
        spin_length.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        def lancer_calcul():
            try:
                auto1 = Automate.charger(combo1.get())
                auto2 = Automate.charger(combo2.get())
                max_len = int(spin_length.get())
                mots = auto1.union_mots(auto2, max_len)
                resultat = "\n".join(sorted(mots, key=lambda x: (len(x), x))[:1000])
                supplement = f"\n...{len(mots) - resultat.count('\n')} mots supplémentaires" if len(mots) > resultat.count('\n') else ""
                messagebox.showinfo("Résultat", f"{len(mots)} mots trouvés (longueur ≤ {max_len}):\n\n{resultat}{supplement}", parent=top)
            except Exception as e:
                messagebox.showerror("Erreur", str(e), parent=top)
        
        ttk.Button(top, text="Calculer l'union", command=lancer_calcul).grid(row=3, columnspan=2, pady=10)

    def calculer_intersection(self):
        """Calcule l'intersection des mots acceptés par deux automates."""
        fichiers = list(Path("automates").glob("*.json"))
        noms = [f.stem for f in fichiers]
        if len(noms) < 2:
            messagebox.showerror("Erreur", "Besoin d'au moins 2 automates", parent=self.root)
            return
        top = tk.Toplevel(self.root)
        top.title("Intersection d'automates")
        top.geometry("400x200")
        
        ttk.Label(top, text="Automate 1:").grid(row=0, column=0, padx=5, pady=5)
        combo1 = ttk.Combobox(top, values=noms, state="readonly")
        combo1.current(0)
        combo1.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Automate 2:").grid(row=1, column=0, padx=5, pady=5)
        combo2 = ttk.Combobox(top, values=noms, state="readonly")
        combo2.current(1 if len(noms) > 1 else 0)
        combo2.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(top, text="Longueur max:").grid(row=2, column=0, padx=5, pady=5)
        spin_length = ttk.Spinbox(top, from_=1, to=10, width=5)
        spin_length.set(5)
        spin_length.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        
        def lancer_calcul():
            try:
                auto1 = Automate.charger(combo1.get())
                auto2 = Automate.charger(combo2.get())
                max_len = int(spin_length.get())
                mots = auto1.intersection_mots(auto2, max_len)
                resultat = "\n".join(sorted(mots, key=lambda x: (len(x), x)))
                messagebox.showinfo("Résultat", f"{len(mots)} mots communs trouvés (longueur ≤ {max_len}):\n{resultat}", parent=top)
            except Exception as e:
                messagebox.showerror("Erreur", str(e), parent=top)
        
        ttk.Button(top, text="Calculer l'intersection", command=lancer_calcul).grid(row=3, columnspan=2, pady=10)

    def calculer_complement(self):
        """Calcule le complément de l'automate actuel (pas encore implémenté)."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné.", parent=self.root)
            return
        messagebox.showinfo("Résultat", "Fonctionnalité de complément non implémentée.", parent=self.root)

    def afficher_infos_securite(self):
        """Affiche un résumé des informations de sécurité pour les automates."""
        try:
            automates = list(Path("automates").glob("*.json"))
            if not automates:
                messagebox.showinfo("Sécurité", "Aucun automate trouvé dans le dossier 'automates'.", parent=self.root)
                return

            protected_automates = []
            for automate_file in automates:
                nom = automate_file.stem
                try:
                    has_password = self.security.verify_password(nom, "") is not None
                    if has_password:
                        mod_time = datetime.fromtimestamp(automate_file.stat().st_mtime)
                        protected_automates.append(f"- {nom} (Dernière modification: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
                except Exception:
                    continue

            total_automates = len(automates)
            total_protected = len(protected_automates)
            message = [
                "=== Résumé de la sécurité ===",
                f"Total automates: {total_automates}",
                f"Automates protégés par mot de passe: {total_protected}",
                "\nAutomates protégés:"
            ]
            if protected_automates:
                message.extend(protected_automates)
            else:
                message.append("- Aucun automate protégé trouvé.")

            messagebox.showinfo("Sécurité", "\n".join(message), parent=self.root)

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de récupérer les infos de sécurité: {str(e)}", parent=self.root)

    def changer_mot_de_passe(self):
        """Change le mot de passe de l'automate actuel."""
        if not self.automate_courant:
            messagebox.showerror("Erreur", "Aucun automate sélectionné", parent=self.root)
            return
        
        old_password = simpledialog.askstring("Authentification", 
                                           "Entrez l'ancien mot de passe:", 
                                           parent=self.root, show='*')
        if not old_password:
            return
        
        if not self.security.verify_password(self.automate_courant.nom, old_password):
            messagebox.showerror("Erreur", "Mot de passe incorrect", parent=self.root)
            return
        
        new_password = simpledialog.askstring("Changer mot de passe", 
                                           "Entrez le nouveau mot de passe:", 
                                           parent=self.root, show='*')
        if not new_password:
            return
        
        confirm_password = simpledialog.askstring("Confirmation", 
                                               "Confirmez le nouveau mot de passe:", 
                                               parent=self.root, show='*')
        if new_password != confirm_password:
            messagebox.showerror("Erreur", "Les mots de passe ne correspondent pas", parent=self.root)
            return
        
        self.security.save_credentials(self.automate_courant.nom, new_password)
        messagebox.showinfo("Succès", "Mot de passe changé avec succès", parent=self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernAutomateApp(root)
    root.mainloop()