#!/usr/bin/env python3
"""
AUTOMAZIONI EXCEL - VERSIONE XLWINGS
Usa Excel direttamente per mantenere TUTTO: menu a tendina, collegamenti, formule, macro

REQUISITI:
pip install xlwings

IMPORTANTE: Richiede Excel installato su Windows
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import xlwings as xw
import os
import datetime
from pathlib import Path
import shutil

class AutomazioniFornitori:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Automazioni Excel - Versione xlwings")
        self.window.geometry("650x680")  # Aumentata per 5 pulsanti
        self.window.resizable(False, False)
        
        self.file_path = tk.StringVar()
        self.setup_ui()
        
    def setup_ui(self):
        """Crea l'interfaccia grafica"""
        
        main_frame = tk.Frame(self.window, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titolo
        title = tk.Label(
            main_frame,
            text="🔧 AUTOMAZIONI EXCEL",
            font=('Arial', 20, 'bold'),
            bg='#f0f0f0',
            fg='#1F3864'
        )
        title.pack(pady=(0, 20))
        
        # Frame selezione file
        file_frame = tk.LabelFrame(
            main_frame,
            text="📂 Seleziona file Excel",
            font=('Arial', 10, 'bold'),
            bg='#f0f0f0',
            padx=10,
            pady=10
        )
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path,
            font=('Arial', 10),
            state='readonly',
            width=55
        )
        file_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = tk.Button(
            file_frame,
            text="Sfoglia...",
            command=self.browse_file,
            font=('Arial', 10),
            bg='#4472C4',
            fg='white',
            cursor='hand2',
            padx=20
        )
        browse_btn.pack(side=tk.LEFT)
        
        # Frame pulsanti
        buttons_frame = tk.Frame(main_frame, bg='#f0f0f0')
        buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # PULSANTE 1
        btn1_frame = tk.Frame(buttons_frame, bg='#4472C4', relief=tk.RAISED, bd=2)
        btn1_frame.pack(fill=tk.X, pady=8)
        
        btn1 = tk.Button(
            btn1_frame,
            text="📊 FERRAMENTA",
            command=self.crea_fogli_fornitori,
            font=('Arial', 13, 'bold'),
            bg='#4472C4',
            fg='white',
            cursor='hand2',
            height=2
        )
        btn1.pack(fill=tk.X, padx=2, pady=2)
        
        desc1 = tk.Label(
            buttons_frame,
            text="Crea un foglio per ogni fornitore (righe 121-202)",
            font=('Arial', 9, 'italic'),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc1.pack()
        
        # PULSANTE 2
        btn_ill_frame = tk.Frame(buttons_frame, bg='#FFC000', relief=tk.RAISED, bd=2)
        btn_ill_frame.pack(fill=tk.X, pady=8)
        
        btn_ill = tk.Button(
            btn_ill_frame,
            text="💡 ILLUMINAZIONE FORNITORI",
            command=self.crea_fogli_illuminazione,
            font=('Arial', 13, 'bold'),
            bg='#FFC000',
            fg='white',
            cursor='hand2',
            height=2
        )
        btn_ill.pack(fill=tk.X, padx=2, pady=2)
        
        desc_ill = tk.Label(
            buttons_frame,
            text="Crea fogli illuminazione (righe 222-240)",
            font=('Arial', 9, 'italic'),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc_ill.pack()
        
        # PULSANTE 3
        btn2_frame = tk.Frame(buttons_frame, bg='#70AD47', relief=tk.RAISED, bd=2)
        btn2_frame.pack(fill=tk.X, pady=8)
        
        btn2 = tk.Button(
            btn2_frame,
            text="📋 SEZIONATURA",
            command=self.raggruppa_sezione,
            font=('Arial', 13, 'bold'),
            bg='#70AD47',
            fg='white',
            cursor='hand2',
            height=2
        )
        btn2.pack(fill=tk.X, padx=2, pady=2)
        
        desc2 = tk.Label(
            buttons_frame,
            text="Raggruppa pezzi con L, H, Materiale identici",
            font=('Arial', 9, 'italic'),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc2.pack()
        
        # PULSANTE 4 - LACCATURA
        btn_lacc_frame = tk.Frame(buttons_frame, bg='#E67E22', relief=tk.RAISED, bd=2)
        btn_lacc_frame.pack(fill=tk.X, pady=8)
        
        btn_lacc = tk.Button(
            btn_lacc_frame,
            text="🎨 LACCATURA",
            command=self.crea_foglio_laccatura,
            font=('Arial', 13, 'bold'),
            bg='#E67E22',
            fg='white',
            cursor='hand2',
            height=2
        )
        btn_lacc.pack(fill=tk.X, padx=2, pady=2)
        
        desc_lacc = tk.Label(
            buttons_frame,
            text="Filtra colonne LACC/TINT/VERN dal foglio GENERALE",
            font=('Arial', 9, 'italic'),
            bg='#f0f0f0',
            fg='#666666'
        )
        desc_lacc.pack()
        
        # PULSANTE 5 - COMPLETO
        btn3_frame = tk.Frame(buttons_frame, bg='#FF6B35', relief=tk.RAISED, bd=2)
        btn3_frame.pack(fill=tk.X, pady=8)
        
        btn3 = tk.Button(
            btn3_frame,
            text="⚡ TUTTO (FERR. + ILLUM. + SEZ. + LACC.)",
            command=self.elaborazione_completa,
            font=('Arial', 13, 'bold'),
            bg='#FF6B35',
            fg='white',
            cursor='hand2',
            height=2
        )
        btn3.pack(fill=tk.X, padx=2, pady=2)
        
        desc3 = tk.Label(
            buttons_frame,
            text="⭐ Esegue TUTTE E 4 le operazioni → 1 file con tutto",
            font=('Arial', 9, 'bold'),
            bg='#f0f0f0',
            fg='#FF6B35'
        )
        desc3.pack()
        
        # Footer
        footer = tk.Label(
            main_frame,
            text="✅ Usa Excel direttamente • ✅ Mantiene TUTTO (menu a tendina, collegamenti, macro)",
            font=('Arial', 8),
            bg='#f0f0f0',
            fg='#999999'
        )
        footer.pack(side=tk.BOTTOM, pady=(15, 0))
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Seleziona il file Excel",
            filetypes=[("File Excel", "*.xlsx *.xlsm"), ("Tutti i file", "*.*")]
        )
        if filename:
            self.file_path.set(filename)
    
    def check_file(self):
        if not self.file_path.get():
            messagebox.showerror("Errore", "Seleziona prima un file Excel!")
            return False
        return True
    
    def crea_copia_e_apri(self, suffisso):
        """Crea copia del file in Downloads e la apre con xlwings"""
        downloads = str(Path.home() / "Downloads")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(os.path.basename(self.file_path.get()))[0]
        ext = os.path.splitext(self.file_path.get())[1]
        filename = f"{base_name}_{suffisso}_{timestamp}{ext}"
        dest_path = os.path.join(downloads, filename)
        
        # Copia TUTTO il file
        shutil.copy2(self.file_path.get(), dest_path)
        
        # Apri con xlwings (Excel)
        wb = xw.Book(dest_path)
        
        return wb, dest_path, filename
    
    def crea_fogli_fornitori(self):
        """FUNZIONE 1: Crea fogli per ogni fornitore"""
        
        if not self.check_file():
            return
        
        try:
            wb, dest_path, filename = self.crea_copia_e_apri("FORNITORI")
            
            ws_main = wb.sheets[0]
            fornitori = {}
            
            # Raccogli fornitori (righe 121-202)
            for r in range(121, 203):
                desc = str(ws_main.range(f'C{r}').value or "").strip()
                forn = str(ws_main.range(f'E{r}').value or "").strip()
                
                if forn and desc:
                    if forn not in fornitori:
                        fornitori[forn] = []
                    
                    cod = str(ws_main.range(f'B{r}').value or "").strip()
                    qta = ws_main.range(f'D{r}').value or 0
                    prz = ws_main.range(f'F{r}').value or 0
                    
                    try:
                        qta = float(qta)
                    except:
                        qta = 0
                    
                    try:
                        prz = float(prz)
                    except:
                        prz = 0
                    
                    if qta > 0:
                        fornitori[forn].append({'cod': cod, 'desc': desc, 'qta': qta, 'prz': prz})
            
            if not fornitori:
                wb.close()
                os.remove(dest_path)
                messagebox.showwarning("Attenzione", "Nessun fornitore trovato (righe 121-202)")
                return
            
            # Crea fogli
            for forn, articoli in fornitori.items():
                # Pulisci nome
                forn_clean = forn
                for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    forn_clean = forn_clean.replace(char, '_')
                forn_clean = forn_clean[:31]
                
                # Cancella se esiste
                if forn_clean in [s.name for s in wb.sheets]:
                    wb.sheets[forn_clean].delete()
                
                # Crea nuovo
                ws = wb.sheets.add(forn_clean)
                
                # Header
                ws.range('A1').value = ['CODICE', 'DESCRIZIONE', 'Q.TA', '€/CAD', '€ TOT.']
                ws.range('A1:E1').api.Font.Bold = True
                ws.range('A1:E1').api.Font.Size = 12
                ws.range('A1:E1').color = (216, 228, 188)  # Verde chiaro
                ws.range('A1:E1').api.HorizontalAlignment = -4108  # Center
                
                # Larghezze
                ws.range('A:A').column_width = 15
                ws.range('B:B').column_width = 65
                ws.range('C:C').column_width = 8
                ws.range('D:D').column_width = 12
                ws.range('E:E').column_width = 14
                
                # Aggrega
                agg = {}
                for art in articoli:
                    if art['desc'] in agg:
                        agg[art['desc']]['qta'] += art['qta']
                    else:
                        agg[art['desc']] = art.copy()
                
                # Scrivi dati
                row = 2
                for art in agg.values():
                    ws.range(f'A{row}').value = art['cod']
                    ws.range(f'A{row}').number_format = '@'
                    ws.range(f'B{row}').value = art['desc']
                    ws.range(f'C{row}').value = art['qta']
                    ws.range(f'D{row}').value = art['prz']
                    ws.range(f'D{row}').number_format = '#,##0.000 €'
                    ws.range(f'E{row}').formula = f'=C{row}*D{row}'
                    ws.range(f'E{row}').number_format = '#,##0.00 €'
                    row += 1
                
                # Totale
                ws.range(f'A{row}').value = 'TOTALE'
                ws.range(f'A{row}').api.Font.Bold = True
                ws.range(f'A{row}').api.Font.Size = 12
                ws.range(f'C{row}').formula = f'=SUM(C2:C{row-1})'
                ws.range(f'C{row}').api.Font.Bold = True
                ws.range(f'E{row}').formula = f'=SUM(E2:E{row-1})'
                ws.range(f'E{row}').number_format = '#,##0.00 €'
                ws.range(f'E{row}').api.Font.Bold = True
                ws.range(f'A{row}:E{row}').color = (216, 228, 188)
            
            # Salva e chiudi
            wb.save()
            wb.close()
            
            messagebox.showinfo(
                "✅ Completato!",
                f"Fogli creati: {len(fornitori)}\n\n📁 {filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Errore", f"{str(e)}")
    
    def crea_fogli_illuminazione(self):
        """FUNZIONE 2: Crea fogli illuminazione"""
        
        if not self.check_file():
            return
        
        try:
            wb, dest_path, filename = self.crea_copia_e_apri("ILLUMINAZIONE")
            
            # Cerca foglio GENERALE
            ws_main = None
            for ws in wb.sheets:
                if ws.name.upper() == "GENERALE":
                    ws_main = ws
                    break
            
            if not ws_main:
                ws_main = wb.sheets[0]
            
            fornitori = {}
            
            # Righe 222-240
            for r in range(222, 241):
                desc = str(ws_main.range(f'C{r}').value or "").strip()
                forn = str(ws_main.range(f'E{r}').value or "").strip()
                
                if forn and desc:
                    if forn not in fornitori:
                        fornitori[forn] = []
                    
                    cod = str(ws_main.range(f'B{r}').value or "").strip()  # Colonna 2
                    qta = ws_main.range(f'D{r}').value or 0
                    prz = ws_main.range(f'F{r}').value or 0
                    
                    try:
                        qta = float(qta)
                    except:
                        qta = 0
                    try:
                        prz = float(prz)
                    except:
                        prz = 0
                    
                    if qta > 0:
                        fornitori[forn].append({'cod': cod, 'desc': desc, 'qta': qta, 'prz': prz})
            
            if not fornitori:
                wb.close()
                os.remove(dest_path)
                messagebox.showwarning("Attenzione", "Nessun fornitore trovato (righe 222-240)")
                return
            
            # Crea fogli
            for forn, articoli in fornitori.items():
                forn_clean = forn
                for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    forn_clean = forn_clean.replace(char, '_')
                sheet_name = (forn_clean + "_ILL")[:31]
                
                if sheet_name in [s.name for s in wb.sheets]:
                    wb.sheets[sheet_name].delete()
                
                ws = wb.sheets.add(sheet_name)
                
                # Header
                ws.range('A1').value = ['CODICE', 'DESCRIZIONE', 'Q.TA', '€/CAD', '€ TOT.']
                ws.range('A1:E1').api.Font.Bold = True
                ws.range('A1:E1').api.Font.Size = 12
                ws.range('A1:E1').color = (255, 242, 204)  # Giallo
                ws.range('A1:E1').api.HorizontalAlignment = -4108
                
                ws.range('A:A').column_width = 22
                ws.range('B:B').column_width = 65
                ws.range('C:C').column_width = 8
                ws.range('D:D').column_width = 12
                ws.range('E:E').column_width = 14
                
                agg = {}
                for art in articoli:
                    if art['desc'] in agg:
                        agg[art['desc']]['qta'] += art['qta']
                    else:
                        agg[art['desc']] = art.copy()
                
                row = 2
                for art in agg.values():
                    ws.range(f'A{row}').value = art['cod']
                    ws.range(f'A{row}').number_format = '@'
                    ws.range(f'B{row}').value = art['desc']
                    ws.range(f'C{row}').value = art['qta']
                    ws.range(f'D{row}').value = art['prz']
                    ws.range(f'D{row}').number_format = '#,##0.000 €'
                    ws.range(f'E{row}').value = art['qta'] * art['prz']
                    ws.range(f'E{row}').number_format = '#,##0.00 €'
                    row += 1
                
                ws.range(f'A{row}').value = 'TOTALE'
                ws.range(f'A{row}').api.Font.Bold = True
                ws.range(f'A{row}').api.Font.Size = 12
                ws.range(f'C{row}').formula = f'=SUM(C2:C{row-1})'
                ws.range(f'C{row}').api.Font.Bold = True
                ws.range(f'E{row}').formula = f'=SUM(E2:E{row-1})'
                ws.range(f'E{row}').number_format = '#,##0.00 €'
                ws.range(f'E{row}').api.Font.Bold = True
                ws.range(f'A{row}:E{row}').color = (255, 242, 204)
            
            wb.save()
            wb.close()
            
            messagebox.showinfo(
                "✅ Completato!",
                f"Fogli illuminazione: {len(fornitori)}\n\n📁 {filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Errore", f"{str(e)}")
    
    def raggruppa_sezione(self):
        """FUNZIONE 3: Raggruppa sezione"""
        
        if not self.check_file():
            return
        
        try:
            wb, dest_path, filename = self.crea_copia_e_apri("RAGGRUPPATO")
            
            # Cerca SEZIONATURA in tutti i fogli
            ws_gen = None
            sez_row, sez_col = 0, 0
            
            for ws in wb.sheets:
                if ws.name == "SEZ. RAGGRUPPATA":
                    continue
                
                # Cerca in tutte le celle
                used_range = ws.used_range
                for row in range(1, used_range.last_cell.row + 1):
                    for col in range(1, used_range.last_cell.column + 1):
                        val = ws.range((row, col)).value
                        if val and str(val).strip().upper() == "SEZIONATURA":
                            ws_gen = ws
                            sez_row = row
                            sez_col = col
                            break
                    if ws_gen:
                        break
                if ws_gen:
                    break
            
            if not ws_gen:
                wb.close()
                os.remove(dest_path)
                messagebox.showerror("Errore", "SEZIONATURA non trovata!")
                return
            
            # Trova inizio dati (2 righe dopo SEZIONATURA)
            data_start = sez_row + 2
            
            # Trova ultima riga con dati
            last_row = data_start
            for r in range(data_start, ws_gen.used_range.last_cell.row + 1):
                has_data = False
                for c in range(sez_col, min(sez_col + 7, ws_gen.used_range.last_cell.column + 1)):
                    if ws_gen.range((r, c)).value:
                        has_data = True
                        break
                if has_data:
                    last_row = r
                else:
                    break
            
            # Raggruppa
            raggruppati = {}
            order = []
            
            for r in range(data_start, last_row + 1):
                L = ws_gen.range((r, sez_col)).value
                H = ws_gen.range((r, sez_col + 1)).value
                QTA = ws_gen.range((r, sez_col + 2)).value or 0
                MAT = str(ws_gen.range((r, sez_col + 3)).value or "")
                PEZZO = str(ws_gen.range((r, sez_col + 4)).value or "")
                CODICE = str(ws_gen.range((r, sez_col + 5)).value or "")
                MOBILE = str(ws_gen.range((r, sez_col + 6)).value or "")
                
                if not L and not H and not MAT:
                    continue
                
                key = f"{L}|{H}|{MAT}"
                
                if key not in raggruppati:
                    raggruppati[key] = {
                        'L': str(L or ""),
                        'H': str(H or ""),
                        'QTA': 0,
                        'MAT': MAT,
                        'CODICE': "",
                        'PEZZO': "",
                        'MOBILE': ""
                    }
                    order.append(key)
                
                try:
                    qta_num = int(QTA) if QTA else 0
                except:
                    qta_num = 0
                
                raggruppati[key]['QTA'] += qta_num
                
                if CODICE:
                    if raggruppati[key]['CODICE']:
                        raggruppati[key]['CODICE'] += " + " + CODICE
                    else:
                        raggruppati[key]['CODICE'] = CODICE
                
                if PEZZO:
                    if raggruppati[key]['PEZZO']:
                        raggruppati[key]['PEZZO'] += " | " + PEZZO
                    else:
                        raggruppati[key]['PEZZO'] = PEZZO
                
                if MOBILE and MOBILE not in raggruppati[key]['MOBILE']:
                    if raggruppati[key]['MOBILE']:
                        raggruppati[key]['MOBILE'] += " | " + MOBILE
                    else:
                        raggruppati[key]['MOBILE'] = MOBILE
            
            # Crea foglio raggruppato
            if "SEZ. RAGGRUPPATA" in [s.name for s in wb.sheets]:
                wb.sheets["SEZ. RAGGRUPPATA"].delete()
            
            ws_dst = wb.sheets.add("SEZ. RAGGRUPPATA")
            
            # Titolo
            ws_dst.range('A1:G1').merge()
            ws_dst.range('A1').value = f"SEZIONATURA RAGGRUPPATA - {ws_gen.name}"
            ws_dst.range('A1').api.Font.Bold = True
            ws_dst.range('A1').api.Font.Size = 13
            ws_dst.range('A1').api.Font.Color = 16777215  # Bianco
            ws_dst.range('A1').color = (31, 56, 100)  # Blu scuro
            ws_dst.range('A1').api.HorizontalAlignment = -4108
            ws_dst.range('A1').api.VerticalAlignment = -4108
            ws_dst.range('A1').row_height = 22
            
            # Header
            headers = ['L.(MM)', 'H.(MM)', "Q.TA'", 'MATERIALE', 'CODICE/I', 'PEZZO/I', 'MOBILE/I']
            ws_dst.range('A2').value = [headers]
            ws_dst.range('A2:G2').api.Font.Bold = True
            ws_dst.range('A2:G2').api.Font.Color = 16777215
            ws_dst.range('A2:G2').color = (31, 78, 121)
            ws_dst.range('A2:G2').api.HorizontalAlignment = -4108
            
            # Larghezze
            ws_dst.range('A:A').column_width = 10
            ws_dst.range('B:B').column_width = 10
            ws_dst.range('C:C').column_width = 8
            ws_dst.range('D:D').column_width = 32
            ws_dst.range('E:E').column_width = 22
            ws_dst.range('F:F').column_width = 50
            ws_dst.range('G:G').column_width = 30
            
            # Dati
            row = 3
            for idx, key in enumerate(order):
                data = raggruppati[key]
                is_merged = ' + ' in data['CODICE']
                
                values = [data['L'], data['H'], data['QTA'], data['MAT'], 
                         data['CODICE'], data['PEZZO'], data['MOBILE']]
                
                ws_dst.range(f'A{row}').value = [values]
                ws_dst.range(f'A{row}:G{row}').api.Font.Size = 9
                
                if is_merged:
                    ws_dst.range(f'A{row}:G{row}').color = (214, 228, 240)  # Blu chiaro
                    ws_dst.range(f'A{row}:G{row}').api.Font.Bold = True
                    ws_dst.range(f'A{row}:G{row}').api.Font.Color = 2105407  # Blu scuro
                elif idx % 2 == 0:
                    ws_dst.range(f'A{row}:G{row}').color = (242, 247, 251)  # Grigio chiaro
                
                # Allineamento
                ws_dst.range(f'A{row}:C{row}').api.HorizontalAlignment = -4108  # Center
                ws_dst.range(f'D{row}:G{row}').api.HorizontalAlignment = -4131  # Left
                
                ws_dst.range(f'A{row}:G{row}').row_height = 14
                row += 1
            
            # Nota
            row += 1
            ws_dst.range(f'A{row}:G{row}').merge()
            ws_dst.range(f'A{row}').value = "Righe in blu = pezzi accorpati (L, H, Materiale identici) -> Q.TA sommata, Codici con +"
            ws_dst.range(f'A{row}').api.Font.Italic = True
            ws_dst.range(f'A{row}').api.Font.Size = 9
            ws_dst.range(f'A{row}').api.Font.Color = 2105407
            
            wb.save()
            wb.close()
            
            messagebox.showinfo(
                "✅ Completato!",
                f"Righe: {len(order)}\nFoglio: {ws_gen.name}\n\n📁 {filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Errore", f"{str(e)}")
    
    def crea_foglio_laccatura(self):
        """FUNZIONE 4: Crea foglio LACCATURA filtrando colonne LACC/TINT/VERN"""
        
        if not self.check_file():
            return
        
        try:
            wb, dest_path, filename = self.crea_copia_e_apri("LACCATURA")
            
            # Cerca foglio GENERALE (case-insensitive)
            ws_src = None
            for ws in wb.sheets:
                if "GENERALE" in ws.name.upper():
                    ws_src = ws
                    break
            
            if not ws_src:
                ws_src = wb.sheets[0]
            
            # DEBUG: Mostra info
            debug_msg = f"DEBUG LACCATURA:\n\n"
            debug_msg += f"Foglio usato: {ws_src.name}\n\n"
            
            HEADER_ROW = 3
            DATA_START_ROW = 4
            keywords = ["LACC", "TINT", "VERN"]
            palette = [
                (255, 199, 206), (255, 235, 156), (198, 239, 206),
                (189, 215, 238), (228, 223, 236), (252, 213, 180)
            ]
            
            # Trova ultima riga e colonna
            last_row = ws_src.range('A' + str(ws_src.cells.last_cell.row)).end('up').row
            # IMPORTANTE: Usa il max della riga 3 per trovare tutte le colonne (non fermarsi alle vuote)
            last_col = ws_src.used_range.last_cell.column
            
            # Trova colonne che contengono keywords nelle righe 1+2+3 combinate (come VBA originale)
            match_cols = []
            for j in range(1, last_col + 1):
                r1 = str(ws_src.range((1, j)).value or "")
                r2 = str(ws_src.range((2, j)).value or "")
                r3 = str(ws_src.range((HEADER_ROW, j)).value or "")
                header_text = (r1 + " " + r2 + " " + r3).upper()
                
                for kw in keywords:
                    if kw in header_text:
                        match_cols.append(j)
                        break
            
            # DEBUG: Mostra colonne trovate
            debug_msg += f"Colonne trovate: {len(match_cols)}\n"
            if match_cols:
                debug_msg += "\nColonne con LACC/TINT/VERN:\n"
                for col in match_cols[:5]:  # Prime 5
                    h1 = ws_src.range((1, col)).value or ""
                    h2 = ws_src.range((2, col)).value or ""
                    h3 = ws_src.range((HEADER_ROW, col)).value or ""
                    debug_msg += f"  Col {col}: '{h1}' '{h2}' '{h3}'\n"
                if len(match_cols) > 5:
                    debug_msg += f"  ... e altre {len(match_cols) - 5}\n"
            else:
                debug_msg += "\n⚠️ NESSUNA COLONNA TROVATA!\n\n"
                debug_msg += f"Last_col rilevato: {last_col}\n\n"
                debug_msg += "Colonne 1-20 (TUTTE E 3 LE RIGHE):\n"
                for j in range(1, min(21, last_col + 1)):
                    r1 = str(ws_src.range((1, j)).value or "")[:20]
                    r2 = str(ws_src.range((2, j)).value or "")[:20]
                    r3 = str(ws_src.range((HEADER_ROW, j)).value or "")[:20]
                    combined = (r1 + " " + r2 + " " + r3).upper()
                    
                    # Indica se contiene keyword
                    has_kw = ""
                    for kw in keywords:
                        if kw in combined:
                            has_kw = f" ← {kw}!"
                            break
                    
                    debug_msg += f"Col {j}: R1:'{r1}' R2:'{r2}' R3:'{r3}'{has_kw}\n"
            
            messagebox.showinfo("DEBUG LACCATURA", debug_msg)
            
            if not match_cols:
                wb.close()
                os.remove(dest_path)
                messagebox.showwarning("Attenzione", "Nessuna colonna LACC/TINT/VERN trovata!")
                return
            
            # Cancella foglio se esiste
            if "LACCATURA" in [s.name for s in wb.sheets]:
                wb.sheets["LACCATURA"].delete()
            
            ws_dst = wb.sheets.add("LACCATURA", after=ws_src)
            
            # Raccogli dati
            temp_data = []
            col_used = [False] * len(match_cols)
            
            debug_rows_checked = 0
            debug_rows_with_data = 0
            
            for i in range(DATA_START_ROW, last_row + 1):
                debug_rows_checked += 1
                if str(ws_src.range((i, 1)).value or "").strip():
                    has_value = False
                    tmp_extra = []
                    
                    for k_idx, col in enumerate(match_cols):
                        v = ws_src.range((i, col)).value
                        if v and ((isinstance(v, (int, float)) and v != 0) or str(v).strip()):
                            has_value = True
                            tmp_extra.append(v)
                            col_used[k_idx] = True
                        else:
                            tmp_extra.append("")
                    
                    if has_value:
                        debug_rows_with_data += 1
                        row_data = []
                        for j in range(1, 9):  # Prime 8 colonne
                            row_data.append(ws_src.range((i, j)).value)
                        row_data.extend(tmp_extra)
                        temp_data.append(row_data)
            
            # DEBUG
            messagebox.showinfo("DEBUG DATI", 
                f"Righe controllate: {debug_rows_checked}\n"
                f"Righe con dati LACC/TINT/VERN: {debug_rows_with_data}\n"
                f"Temp_data raccolte: {len(temp_data)}")
            
            # Filtra solo colonne usate
            final_extra_idx = [i for i, used in enumerate(col_used) if used]
            
            if not final_extra_idx:
                wb.close()
                os.remove(dest_path)
                messagebox.showwarning("Attenzione", "Nessun dato trovato nelle colonne LACC/TINT/VERN!")
                return
            
            total_cols = 8 + len(final_extra_idx)
            
            # Scrivi header
            for j in range(1, 9):
                ws_dst.range((1, j)).value = ws_src.range((HEADER_ROW, j)).value
            
            for k_idx, orig_idx in enumerate(final_extra_idx):
                ws_dst.range((1, 8 + k_idx + 1)).value = ws_src.range((HEADER_ROW, match_cols[orig_idx])).value
            
            # Scrivi dati
            out_row = 2
            for row_data in temp_data:
                for j in range(8):
                    ws_dst.range((out_row, j + 1)).value = row_data[j]
                for k_idx, orig_idx in enumerate(final_extra_idx):
                    ws_dst.range((out_row, 8 + k_idx + 1)).value = row_data[8 + orig_idx]
                out_row += 1
            
            last_data_row = out_row - 1
            
            # Formatta header
            header_range = ws_dst.range((1, 1), (1, total_cols))
            header_range.api.Font.Bold = True
            header_range.api.Font.Size = 12
            header_range.api.HorizontalAlignment = -4108
            header_range.api.VerticalAlignment = -4108
            header_range.row_height = 28
            
            # Colora header colonne extra
            for k_idx in range(len(final_extra_idx)):
                ws_dst.range((1, 8 + k_idx + 1)).color = palette[k_idx % len(palette)]
            
            # Colora righe in base a quale colonna ha valore
            for i in range(2, last_data_row + 1):
                for k_idx in range(len(final_extra_idx)):
                    cell_val = ws_dst.range((i, 8 + k_idx + 1)).value
                    if cell_val and ((isinstance(cell_val, (int, float)) and cell_val != 0) or str(cell_val).strip()):
                        ws_dst.range((i, 1), (i, total_cols)).color = palette[k_idx % len(palette)]
                        break
            
            # Aggiungi riga totale
            ws_dst.range((last_data_row + 1, 1)).value = "TOTALE"
            ws_dst.range((last_data_row + 1, 1)).api.Font.Bold = True
            
            for k_idx in range(len(final_extra_idx)):
                col = 8 + k_idx + 1
                ws_dst.range((last_data_row + 1, col)).formula = f'=SUM({ws_dst.range((2, col)).get_address(False, False)}:{ws_dst.range((last_data_row, col)).get_address(False, False)})'
                ws_dst.range((last_data_row + 1, col)).api.Font.Bold = True
            
            # Formato numero
            for col in range(9, total_cols + 1):
                ws_dst.range((2, col), (last_data_row + 1, col)).number_format = '0.0'
            
            # Freeze panes
            ws_dst.range('A2').select()
            wb.app.api.ActiveWindow.FreezePanes = True
            
            # AutoFit
            ws_dst.autofit()
            
            wb.save()
            wb.close()
            
            messagebox.showinfo(
                "✅ Completato!",
                f"Foglio LACCATURA creato!\n\nRighe: {last_data_row - 1}\nColonne extra: {len(final_extra_idx)}\n\n📁 {filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Errore", f"{str(e)}")
    
    def elaborazione_completa(self):
        """FUNZIONE 4: FERRAMENTA + ILLUMINAZIONE + SEZIONATURA"""
        
        if not self.check_file():
            return
        
        try:
            wb, dest_path, filename = self.crea_copia_e_apri("COMPLETO")
            
            # === PARTE 1: FERRAMENTA ===
            ws_main = wb.sheets[0]
            fornitori = {}
            
            for r in range(121, 203):
                desc = str(ws_main.range(f'C{r}').value or "").strip()
                forn = str(ws_main.range(f'E{r}').value or "").strip()
                
                if forn and desc:
                    if forn not in fornitori:
                        fornitori[forn] = []
                    
                    cod = str(ws_main.range(f'B{r}').value or "").strip()
                    qta = ws_main.range(f'D{r}').value or 0
                    prz = ws_main.range(f'F{r}').value or 0
                    
                    try:
                        qta = float(qta)
                    except:
                        qta = 0
                    try:
                        prz = float(prz)
                    except:
                        prz = 0
                    
                    if qta > 0:
                        fornitori[forn].append({'cod': cod, 'desc': desc, 'qta': qta, 'prz': prz})
            
            fogli_fornitori = 0
            for forn, articoli in fornitori.items():
                forn_clean = forn
                for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    forn_clean = forn_clean.replace(char, '_')
                forn_clean = forn_clean[:31]
                
                if forn_clean in [s.name for s in wb.sheets]:
                    wb.sheets[forn_clean].delete()
                
                ws = wb.sheets.add(forn_clean)
                
                ws.range('A1').value = ['CODICE', 'DESCRIZIONE', 'Q.TA', '€/CAD', '€ TOT.']
                ws.range('A1:E1').api.Font.Bold = True
                ws.range('A1:E1').api.Font.Size = 12
                ws.range('A1:E1').color = (216, 228, 188)
                ws.range('A1:E1').api.HorizontalAlignment = -4108
                
                ws.range('A:A').column_width = 15
                ws.range('B:B').column_width = 65
                ws.range('C:C').column_width = 8
                ws.range('D:D').column_width = 12
                ws.range('E:E').column_width = 14
                
                agg = {}
                for art in articoli:
                    if art['desc'] in agg:
                        agg[art['desc']]['qta'] += art['qta']
                    else:
                        agg[art['desc']] = art.copy()
                
                row = 2
                for art in agg.values():
                    ws.range(f'A{row}').value = art['cod']
                    ws.range(f'A{row}').number_format = '@'
                    ws.range(f'B{row}').value = art['desc']
                    ws.range(f'C{row}').value = art['qta']
                    ws.range(f'D{row}').value = art['prz']
                    ws.range(f'D{row}').number_format = '#,##0.000 €'
                    ws.range(f'E{row}').formula = f'=C{row}*D{row}'
                    ws.range(f'E{row}').number_format = '#,##0.00 €'
                    row += 1
                
                ws.range(f'A{row}').value = 'TOTALE'
                ws.range(f'A{row}').api.Font.Bold = True
                ws.range(f'A{row}').api.Font.Size = 12
                ws.range(f'C{row}').formula = f'=SUM(C2:C{row-1})'
                ws.range(f'C{row}').api.Font.Bold = True
                ws.range(f'E{row}').formula = f'=SUM(E2:E{row-1})'
                ws.range(f'E{row}').number_format = '#,##0.00 €'
                ws.range(f'E{row}').api.Font.Bold = True
                ws.range(f'A{row}:E{row}').color = (216, 228, 188)
                
                fogli_fornitori += 1
            
            # === PARTE 2: ILLUMINAZIONE ===
            ws_ill = None
            for ws in wb.sheets:
                if ws.name.upper() == "GENERALE":
                    ws_ill = ws
                    break
            if not ws_ill:
                ws_ill = ws_main
            
            fornitori_ill = {}
            
            for r in range(222, 241):
                desc = str(ws_ill.range(f'C{r}').value or "").strip()
                forn = str(ws_ill.range(f'E{r}').value or "").strip()
                
                if forn and desc:
                    if forn not in fornitori_ill:
                        fornitori_ill[forn] = []
                    
                    cod = str(ws_ill.range(f'B{r}').value or "").strip()
                    qta = ws_ill.range(f'D{r}').value or 0
                    prz = ws_ill.range(f'F{r}').value or 0
                    
                    try:
                        qta = float(qta)
                    except:
                        qta = 0
                    try:
                        prz = float(prz)
                    except:
                        prz = 0
                    
                    if qta > 0:
                        fornitori_ill[forn].append({'cod': cod, 'desc': desc, 'qta': qta, 'prz': prz})
            
            fogli_illuminazione = 0
            for forn, articoli in fornitori_ill.items():
                forn_clean = forn
                for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
                    forn_clean = forn_clean.replace(char, '_')
                sheet_name = (forn_clean + "_ILL")[:31]
                
                if sheet_name in [s.name for s in wb.sheets]:
                    wb.sheets[sheet_name].delete()
                
                ws = wb.sheets.add(sheet_name)
                
                ws.range('A1').value = ['CODICE', 'DESCRIZIONE', 'Q.TA', '€/CAD', '€ TOT.']
                ws.range('A1:E1').api.Font.Bold = True
                ws.range('A1:E1').api.Font.Size = 12
                ws.range('A1:E1').color = (255, 242, 204)
                ws.range('A1:E1').api.HorizontalAlignment = -4108
                
                ws.range('A:A').column_width = 22
                ws.range('B:B').column_width = 65
                ws.range('C:C').column_width = 8
                ws.range('D:D').column_width = 12
                ws.range('E:E').column_width = 14
                
                agg = {}
                for art in articoli:
                    if art['desc'] in agg:
                        agg[art['desc']]['qta'] += art['qta']
                    else:
                        agg[art['desc']] = art.copy()
                
                row = 2
                for art in agg.values():
                    ws.range(f'A{row}').value = art['cod']
                    ws.range(f'A{row}').number_format = '@'
                    ws.range(f'B{row}').value = art['desc']
                    ws.range(f'C{row}').value = art['qta']
                    ws.range(f'D{row}').value = art['prz']
                    ws.range(f'D{row}').number_format = '#,##0.000 €'
                    ws.range(f'E{row}').value = art['qta'] * art['prz']
                    ws.range(f'E{row}').number_format = '#,##0.00 €'
                    row += 1
                
                ws.range(f'A{row}').value = 'TOTALE'
                ws.range(f'A{row}').api.Font.Bold = True
                ws.range(f'A{row}').api.Font.Size = 12
                ws.range(f'C{row}').formula = f'=SUM(C2:C{row-1})'
                ws.range(f'C{row}').api.Font.Bold = True
                ws.range(f'E{row}').formula = f'=SUM(E2:E{row-1})'
                ws.range(f'E{row}').number_format = '#,##0.00 €'
                ws.range(f'E{row}').api.Font.Bold = True
                ws.range(f'A{row}:E{row}').color = (255, 242, 204)
                
                fogli_illuminazione += 1
            
            # === PARTE 3: SEZIONATURA ===
            ws_gen = None
            sez_row, sez_col = 0, 0
            
            for ws in wb.sheets:
                if ws.name == "SEZ. RAGGRUPPATA":
                    continue
                used_range = ws.used_range
                for row in range(1, used_range.last_cell.row + 1):
                    for col in range(1, used_range.last_cell.column + 1):
                        val = ws.range((row, col)).value
                        if val and str(val).strip().upper() == "SEZIONATURA":
                            ws_gen = ws
                            sez_row = row
                            sez_col = col
                            break
                    if ws_gen:
                        break
                if ws_gen:
                    break
            
            righe_sezione = 0
            
            if ws_gen and sez_col > 0:
                data_start = sez_row + 2
                last_row = data_start
                
                for r in range(data_start, ws_gen.used_range.last_cell.row + 1):
                    has_data = False
                    for c in range(sez_col, min(sez_col + 7, ws_gen.used_range.last_cell.column + 1)):
                        if ws_gen.range((r, c)).value:
                            has_data = True
                            break
                    if has_data:
                        last_row = r
                    else:
                        break
                
                raggruppati = {}
                order = []
                
                for r in range(data_start, last_row + 1):
                    L = ws_gen.range((r, sez_col)).value
                    H = ws_gen.range((r, sez_col + 1)).value
                    QTA = ws_gen.range((r, sez_col + 2)).value or 0
                    MAT = str(ws_gen.range((r, sez_col + 3)).value or "")
                    PEZZO = str(ws_gen.range((r, sez_col + 4)).value or "")
                    CODICE = str(ws_gen.range((r, sez_col + 5)).value or "")
                    MOBILE = str(ws_gen.range((r, sez_col + 6)).value or "")
                    
                    if not L and not H and not MAT:
                        continue
                    
                    key = f"{L}|{H}|{MAT}"
                    
                    if key not in raggruppati:
                        raggruppati[key] = {
                            'L': str(L or ""), 'H': str(H or ""), 'QTA': 0,
                            'MAT': MAT, 'CODICE': "", 'PEZZO': "", 'MOBILE': ""
                        }
                        order.append(key)
                    
                    try:
                        qta_num = int(QTA) if QTA else 0
                    except:
                        qta_num = 0
                    
                    raggruppati[key]['QTA'] += qta_num
                    
                    if CODICE:
                        if raggruppati[key]['CODICE']:
                            raggruppati[key]['CODICE'] += " + " + CODICE
                        else:
                            raggruppati[key]['CODICE'] = CODICE
                    
                    if PEZZO:
                        if raggruppati[key]['PEZZO']:
                            raggruppati[key]['PEZZO'] += " | " + PEZZO
                        else:
                            raggruppati[key]['PEZZO'] = PEZZO
                    
                    if MOBILE and MOBILE not in raggruppati[key]['MOBILE']:
                        if raggruppati[key]['MOBILE']:
                            raggruppati[key]['MOBILE'] += " | " + MOBILE
                        else:
                            raggruppati[key]['MOBILE'] = MOBILE
                
                if "SEZ. RAGGRUPPATA" in [s.name for s in wb.sheets]:
                    wb.sheets["SEZ. RAGGRUPPATA"].delete()
                
                ws_dst = wb.sheets.add("SEZ. RAGGRUPPATA")
                
                ws_dst.range('A1:G1').merge()
                ws_dst.range('A1').value = f"SEZIONATURA RAGGRUPPATA - {ws_gen.name}"
                ws_dst.range('A1').api.Font.Bold = True
                ws_dst.range('A1').api.Font.Size = 13
                ws_dst.range('A1').api.Font.Color = 16777215
                ws_dst.range('A1').color = (31, 56, 100)
                ws_dst.range('A1').api.HorizontalAlignment = -4108
                ws_dst.range('A1').row_height = 22
                
                headers = ['L.(MM)', 'H.(MM)', "Q.TA'", 'MATERIALE', 'CODICE/I', 'PEZZO/I', 'MOBILE/I']
                ws_dst.range('A2').value = [headers]
                ws_dst.range('A2:G2').api.Font.Bold = True
                ws_dst.range('A2:G2').api.Font.Color = 16777215
                ws_dst.range('A2:G2').color = (31, 78, 121)
                ws_dst.range('A2:G2').api.HorizontalAlignment = -4108
                
                ws_dst.range('A:A').column_width = 10
                ws_dst.range('B:B').column_width = 10
                ws_dst.range('C:C').column_width = 8
                ws_dst.range('D:D').column_width = 32
                ws_dst.range('E:E').column_width = 22
                ws_dst.range('F:F').column_width = 50
                ws_dst.range('G:G').column_width = 30
                
                row = 3
                for idx, key in enumerate(order):
                    data = raggruppati[key]
                    is_merged = ' + ' in data['CODICE']
                    
                    values = [data['L'], data['H'], data['QTA'], data['MAT'], 
                             data['CODICE'], data['PEZZO'], data['MOBILE']]
                    
                    ws_dst.range(f'A{row}').value = [values]
                    ws_dst.range(f'A{row}:G{row}').api.Font.Size = 9
                    
                    if is_merged:
                        ws_dst.range(f'A{row}:G{row}').color = (214, 228, 240)
                        ws_dst.range(f'A{row}:G{row}').api.Font.Bold = True
                        ws_dst.range(f'A{row}:G{row}').api.Font.Color = 2105407
                    elif idx % 2 == 0:
                        ws_dst.range(f'A{row}:G{row}').color = (242, 247, 251)
                    
                    ws_dst.range(f'A{row}:C{row}').api.HorizontalAlignment = -4108
                    ws_dst.range(f'D{row}:G{row}').api.HorizontalAlignment = -4131
                    ws_dst.range(f'A{row}:G{row}').row_height = 14
                    row += 1
                
                righe_sezione = len(order)
                
                row += 1
                ws_dst.range(f'A{row}:G{row}').merge()
                ws_dst.range(f'A{row}').value = "Righe in blu = pezzi accorpati → Q.TA sommata, Codici con +"
                ws_dst.range(f'A{row}').api.Font.Italic = True
                ws_dst.range(f'A{row}').api.Font.Size = 9
                ws_dst.range(f'A{row}').api.Font.Color = 2105407
            
            # === PARTE 4: LACCATURA ===
            keywords = ["LACC", "TINT", "VERN"]
            palette_lacc = [
                (255, 199, 206), (255, 235, 156), (198, 239, 206),
                (189, 215, 238), (228, 223, 236), (252, 213, 180)
            ]
            
            # Cerca foglio GENERALE
            ws_lacc = None
            for ws in wb.sheets:
                if "GENERALE" in ws.name.upper():
                    ws_lacc = ws
                    break
            if not ws_lacc:
                ws_lacc = ws_main
            
            HEADER_ROW = 3
            DATA_START_ROW = 4
            
            last_row_lacc = ws_lacc.range('A' + str(ws_lacc.cells.last_cell.row)).end('up').row
            last_col_lacc = ws_lacc.used_range.last_cell.column
            
            match_cols_lacc = []
            for j in range(1, last_col_lacc + 1):
                r1 = str(ws_lacc.range((1, j)).value or "")
                r2 = str(ws_lacc.range((2, j)).value or "")
                r3 = str(ws_lacc.range((HEADER_ROW, j)).value or "")
                header_text = (r1 + " " + r2 + " " + r3).upper()
                
                for kw in keywords:
                    if kw in header_text:
                        match_cols_lacc.append(j)
                        break
            
            righe_laccatura = 0
            
            if match_cols_lacc:
                temp_data_lacc = []
                col_used_lacc = [False] * len(match_cols_lacc)
                
                for i in range(DATA_START_ROW, last_row_lacc + 1):
                    if str(ws_lacc.range((i, 1)).value or "").strip():
                        has_value = False
                        tmp_extra = []
                        
                        for k_idx, col in enumerate(match_cols_lacc):
                            v = ws_lacc.range((i, col)).value
                            if v and ((isinstance(v, (int, float)) and v != 0) or str(v).strip()):
                                has_value = True
                                tmp_extra.append(v)
                                col_used_lacc[k_idx] = True
                            else:
                                tmp_extra.append("")
                        
                        if has_value:
                            row_data = []
                            for j in range(1, 9):
                                row_data.append(ws_lacc.range((i, j)).value)
                            row_data.extend(tmp_extra)
                            temp_data_lacc.append(row_data)
                
                final_extra_idx_lacc = [i for i, used in enumerate(col_used_lacc) if used]
                
                if final_extra_idx_lacc and temp_data_lacc:
                    if "LACCATURA" in [s.name for s in wb.sheets]:
                        wb.sheets["LACCATURA"].delete()
                    
                    ws_dst_lacc = wb.sheets.add("LACCATURA")
                    
                    total_cols_lacc = 8 + len(final_extra_idx_lacc)
                    
                    for j in range(1, 9):
                        ws_dst_lacc.range((1, j)).value = ws_lacc.range((HEADER_ROW, j)).value
                    
                    for k_idx, orig_idx in enumerate(final_extra_idx_lacc):
                        ws_dst_lacc.range((1, 8 + k_idx + 1)).value = ws_lacc.range((HEADER_ROW, match_cols_lacc[orig_idx])).value
                    
                    out_row_lacc = 2
                    for row_data in temp_data_lacc:
                        for j in range(8):
                            ws_dst_lacc.range((out_row_lacc, j + 1)).value = row_data[j]
                        for k_idx, orig_idx in enumerate(final_extra_idx_lacc):
                            ws_dst_lacc.range((out_row_lacc, 8 + k_idx + 1)).value = row_data[8 + orig_idx]
                        out_row_lacc += 1
                    
                    last_data_row_lacc = out_row_lacc - 1
                    righe_laccatura = last_data_row_lacc - 1
                    
                    header_range = ws_dst_lacc.range((1, 1), (1, total_cols_lacc))
                    header_range.api.Font.Bold = True
                    header_range.api.Font.Size = 12
                    header_range.api.HorizontalAlignment = -4108
                    header_range.row_height = 28
                    
                    for k_idx in range(len(final_extra_idx_lacc)):
                        ws_dst_lacc.range((1, 8 + k_idx + 1)).color = palette_lacc[k_idx % len(palette_lacc)]
                    
                    for i in range(2, last_data_row_lacc + 1):
                        for k_idx in range(len(final_extra_idx_lacc)):
                            cell_val = ws_dst_lacc.range((i, 8 + k_idx + 1)).value
                            if cell_val and ((isinstance(cell_val, (int, float)) and cell_val != 0) or str(cell_val).strip()):
                                ws_dst_lacc.range((i, 1), (i, total_cols_lacc)).color = palette_lacc[k_idx % len(palette_lacc)]
                                break
                    
                    ws_dst_lacc.range((last_data_row_lacc + 1, 1)).value = "TOTALE"
                    ws_dst_lacc.range((last_data_row_lacc + 1, 1)).api.Font.Bold = True
                    
                    for k_idx in range(len(final_extra_idx_lacc)):
                        col = 8 + k_idx + 1
                        ws_dst_lacc.range((last_data_row_lacc + 1, col)).formula = f'=SUM({ws_dst_lacc.range((2, col)).get_address(False, False)}:{ws_dst_lacc.range((last_data_row_lacc, col)).get_address(False, False)})'
                        ws_dst_lacc.range((last_data_row_lacc + 1, col)).api.Font.Bold = True
                    
                    for col in range(9, total_cols_lacc + 1):
                        ws_dst_lacc.range((2, col), (last_data_row_lacc + 1, col)).number_format = '0.0'
            
            # === SALVA ===
            wb.save()
            wb.close()
            
            msg = f"⚡ ELABORAZIONE COMPLETA!\n\n"
            msg += f"📊 Fogli ferramenta: {fogli_fornitori}\n"
            msg += f"💡 Fogli illuminazione: {fogli_illuminazione}\n"
            if righe_sezione > 0:
                msg += f"📋 Righe sezione: {righe_sezione}\n"
            else:
                msg += f"⚠️ Sezione non trovata\n"
            if righe_laccatura > 0:
                msg += f"🎨 Righe laccatura: {righe_laccatura}\n"
            else:
                msg += f"⚠️ Laccatura non trovata\n"
            msg += f"\n📁 {filename}"
            
            messagebox.showinfo("✅ Fatto!", msg)
            
        except Exception as e:
            messagebox.showerror("Errore", f"{str(e)}")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = AutomazioniFornitori()
    app.run()
