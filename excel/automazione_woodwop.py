"""
AUTOMAZIONE WOODWOP - Importazione e elaborazione file STEP
Automatizza l'importazione di file .stp/.step in WoodWop
"""

import pyautogui
import time
import json
import os
from pathlib import Path
from tkinter import Tk, filedialog

# Configurazione sicurezza
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5  # Pausa tra i comandi

class WoodWopAutomation:
    def __init__(self):
        self.coordinates = self.load_coordinates()
        
    def load_coordinates(self):
        """Carica le coordinate salvate dalla calibrazione"""
        coord_file = '/home/claude/woodwop_coordinates.json'
        if not os.path.exists(coord_file):
            print("❌ ERRORE: File coordinate non trovato!")
            print("Esegui prima lo script di calibrazione: calibrazione_woodwop.py")
            exit(1)
        
        with open(coord_file, 'r') as f:
            coords = json.load(f)
        
        # Converti in oggetti Point
        return {key: pyautogui.Point(value['x'], value['y']) 
                for key, value in coords.items()}
    
    def click_at(self, coordinate_name, clicks=1, interval=0.0):
        """Clicca su una coordinata salvata"""
        if coordinate_name not in self.coordinates:
            print(f"⚠️  Coordinata '{coordinate_name}' non trovata!")
            return False
        
        pos = self.coordinates[coordinate_name]
        pyautogui.click(pos.x, pos.y, clicks=clicks, interval=interval)
        time.sleep(0.3)
        return True
    
    def type_text(self, text):
        """Digita testo con pyautogui"""
        pyautogui.write(text, interval=0.05)
        time.sleep(0.2)
    
    def press_key(self, key):
        """Premi un tasto"""
        pyautogui.press(key)
        time.sleep(0.2)
    
    def select_folder(self, title):
        """Apre dialog per selezione cartella"""
        root = Tk()
        root.withdraw()  # Nascondi finestra principale
        root.attributes('-topmost', True)  # Porta in primo piano
        
        folder = filedialog.askdirectory(title=title)
        root.destroy()
        
        return folder
    
    def get_step_files(self, folder_path):
        """Ottiene tutti i file .stp e .step dalla cartella"""
        path = Path(folder_path)
        step_files = list(path.glob('*.stp')) + list(path.glob('*.step'))
        return sorted(step_files)
    
    def import_and_process_file(self, file_path, output_folder):
        """Importa ed elabora un singolo file"""
        print(f"\n{'='*60}")
        print(f"Elaborazione: {file_path.name}")
        print(f"{'='*60}")
        
        # 1. Apri menu File
        print("1. Apertura menu File...")
        self.click_at('menu_file')
        time.sleep(0.5)
        
        # 2. Clicca su Importa
        print("2. Click su Importa...")
        self.click_at('menu_importa')
        time.sleep(0.5)
        
        # 3. Clicca su CAD
        print("3. Click su CAD...")
        self.click_at('menu_cad')
        time.sleep(1.0)  # Attendi apertura finestra di dialogo
        
        # 4. Inserisci percorso file
        print("4. Inserimento percorso file...")
        self.click_at('campo_nome_file')
        time.sleep(0.3)
        
        # Seleziona tutto e cancella
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Digita il percorso completo del file
        self.type_text(str(file_path))
        time.sleep(0.5)
        
        # 5. Clicca su Apri
        print("5. Click su Apri...")
        self.click_at('pulsante_apri')
        time.sleep(2.0)  # Attendi caricamento file
        
        # 6. Clicca sulla freccia per procedere
        print("6. Click sulla freccia...")
        self.click_at('freccia_avanti')
        time.sleep(0.5)
        
        # 7. Premi ENTER
        print("7. Pressione ENTER...")
        self.press_key('return')
        time.sleep(1.0)
        
        # 8. Seleziona oggetto nero (click nell'area)
        print("8. Selezione oggetto nero...")
        self.click_at('area_selezione')
        time.sleep(0.5)
        
        # 9. Premi ENTER per confermare selezione
        print("9. Conferma selezione...")
        self.press_key('return')
        time.sleep(0.5)
        
        # 10. Verifica/attiva checkbox flag
        print("10. Verifica flag 'Ruotare automaticamente'...")
        self.click_at('checkbox_flag')
        time.sleep(0.3)
        
        # 11. Premi ENTER finale
        print("11. ENTER finale...")
        self.press_key('return')
        time.sleep(1.0)
        
        # 12. Salva il file
        print("12. Salvataggio file...")
        output_path = Path(output_folder) / f"{file_path.stem}.mpr"
        self.save_file(output_path)
        
        print(f"✓ File elaborato e salvato: {output_path.name}")
    
    def save_file(self, output_path):
        """Salva il file elaborato"""
        # Apri menu File
        self.click_at('menu_file')
        time.sleep(0.5)
        
        # Clicca su Salva con nome
        self.click_at('menu_salva_con_nome')
        time.sleep(1.0)
        
        # Inserisci nome file
        self.click_at('campo_salva_nome')
        time.sleep(0.3)
        
        # Seleziona tutto e sostituisci
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        
        # Digita percorso completo
        self.type_text(str(output_path))
        time.sleep(0.5)
        
        # Clicca su Salva
        self.click_at('pulsante_salva')
        time.sleep(1.0)
    
    def run(self):
        """Esegue l'automazione completa"""
        print("\n" + "="*60)
        print("AUTOMAZIONE WOODWOP - IMPORTAZIONE FILE STEP")
        print("="*60)
        
        # Chiedi cartella di origine
        print("\n1. Seleziona la cartella contenente i file STEP...")
        input_folder = self.select_folder("Seleziona cartella file STEP")
        
        if not input_folder:
            print("❌ Nessuna cartella selezionata. Uscita.")
            return
        
        print(f"✓ Cartella origine: {input_folder}")
        
        # Chiedi cartella di destinazione
        print("\n2. Seleziona la cartella dove salvare i file elaborati...")
        output_folder = self.select_folder("Seleziona cartella di destinazione")
        
        if not output_folder:
            print("❌ Nessuna cartella selezionata. Uscita.")
            return
        
        print(f"✓ Cartella destinazione: {output_folder}")
        
        # Trova tutti i file STEP
        step_files = self.get_step_files(input_folder)
        
        if not step_files:
            print(f"\n❌ Nessun file .stp o .step trovato in {input_folder}")
            return
        
        print(f"\n✓ Trovati {len(step_files)} file da elaborare:")
        for i, f in enumerate(step_files, 1):
            print(f"   {i}. {f.name}")
        
        # Conferma prima di iniziare
        print("\n" + "="*60)
        print("⚠️  L'automazione inizierà tra 5 secondi")
        print("   Assicurati che WoodWop sia aperto e visibile!")
        print("   Muovi il mouse nell'angolo in alto a sinistra per interrompere")
        print("="*60)
        
        for i in range(5, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
        print("\n\n🚀 AVVIO!")
        
        # Elabora ogni file
        success_count = 0
        error_count = 0
        
        for i, file_path in enumerate(step_files, 1):
            try:
                print(f"\n[{i}/{len(step_files)}]", end=" ")
                self.import_and_process_file(file_path, output_folder)
                success_count += 1
            except Exception as e:
                print(f"❌ ERRORE durante elaborazione {file_path.name}: {e}")
                error_count += 1
                # Continua con il prossimo file
                continue
        
        # Riepilogo finale
        print("\n" + "="*60)
        print("AUTOMAZIONE COMPLETATA!")
        print("="*60)
        print(f"✓ File elaborati con successo: {success_count}")
        if error_count > 0:
            print(f"❌ File con errori: {error_count}")
        print(f"\nFile salvati in: {output_folder}")


if __name__ == "__main__":
    automation = WoodWopAutomation()
    automation.run()
