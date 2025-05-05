import os
import io
import sqlite3
import pandas as pd
import requests
import random
import time
import csv
from datetime import datetime, timedelta
from googletrans import Translator

def scarica_dati_meteo():

    url_base = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/italy"
    key_1 = "K3XVL3NJBB5Q3EQUC3WDTEC53"
    key_2 = "YMH9Z6R829Q2BAC43379ZPWVK"

    meteo_file = os.path.join('meteo', 'dati_meteo_italia.csv')
    file_esistente = os.path.exists(meteo_file)

    if file_esistente:
        df_existing = pd.read_csv(meteo_file)
        df_existing = df_existing[df_existing['data'] != 'data']
        df_existing['data'] = pd.to_datetime(df_existing['data'], errors='coerce')
        last_date = df_existing['data'].max()
    else:
        last_date = datetime(2024, 1, 1)

    today = datetime.now() + timedelta(days=14)

    if last_date >= today:
        print("I dati sono già aggiornati.")
        return

    if not file_esistente:
        os.makedirs('meteo', exist_ok=True)
        with open(meteo_file, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["data", "temp", "descrizione", "umidita", "precipitazioni"])

    start_date = last_date + timedelta(days=1)
    translator = Translator()

    while start_date <= today:
        end_date = min(start_date + timedelta(days=29), today)
        print(f"Blocco: {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")

        successo = False

        for key in [key_1, key_2]:
            try:
                request_url = (
                    f"{url_base}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                    f"?unitGroup=metric&include=days&key={key}&contentType=csv"
                )
                response = requests.get(request_url)
                response.raise_for_status()

                lines = response.text.strip().split('\n')
                header = lines[0].split(',')

                idx_data = header.index("datetime")
                idx_temp = header.index("temp")
                idx_descrizione = header.index("description")
                idx_umidita = header.index("humidity")
                idx_precipitazioni = header.index("precip")

                nuovi_dati = []

                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) > max(idx_data, idx_temp, idx_descrizione, idx_umidita, idx_precipitazioni):
                        data = parts[idx_data]
                        temp = float(parts[idx_temp].strip())
                        desc_raw = parts[idx_descrizione].strip().strip('"')
                        descrizione = translator.translate(desc_raw, src='en', dest='it').text
                        umidita = float(parts[idx_umidita].strip())
                        precipitazioni = float(parts[idx_precipitazioni].strip())

                        nuovi_dati.append([
                            data,
                            f"{temp:.1f}°C",
                            descrizione,
                            f"{int(umidita)}%",
                            f"{precipitazioni:.2f} mm"
                        ])

                with open(meteo_file, "a", encoding="utf-8", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerows(nuovi_dati)

                print(f"{len(nuovi_dati)} righe salvate da API con key terminante in {key[-4:]}")
                successo = True
                break

            except requests.exceptions.HTTPError as e:
                print(f"Errore HTTP: {e}")
                if e.response.status_code == 429:
                    print("Limite giornaliero superato, provo altra chiave...")
                else:
                    print("Altro errore HTTP.")
            except Exception as e:
                print(f"Errore generico: {e}")

        if not successo:
            print("Nessuna API disponibile per questo blocco. Interrompo il download.")
            break

        start_date = end_date + timedelta(days=1)
        time.sleep(5)

    print("Download completato e file aggiornato!")


def crea_dati_fittizi_meteo():
    print("Generando dati fittizi basati su quelli reali...")

    try:
        file_input = os.path.join('meteo', "dati_meteo_italia.csv")
        file_output = os.path.join('meteo', "dati_fittizi_meteo.csv")

        if not os.path.exists(file_input):
            print(f"File '{file_input}' non trovato.")
            return

        if os.path.exists(file_output):
            os.remove(file_output)
            print(f"File '{file_output}' esistente eliminato.")

        df = pd.read_csv(file_input, parse_dates=["data"])

        df['temp'] = df['temp'].str.replace("°C", "").astype(float)
        df['umidita'] = df['umidita'].str.replace("%", "").astype(float)
        df['precipitazioni'] = df['precipitazioni'].str.replace(" mm", "").astype(float)
        df['descrizione'] = df['descrizione'].str.strip().str.replace('"', '')

        df = df.dropna(subset=['temp', 'descrizione', 'umidita', 'precipitazioni'])

        temperature = df['temp'].unique()
        umidita_values = df['umidita'].unique()
        precipitazioni_values = df['precipitazioni'].unique()
        descrizioni = df['descrizione'].unique()

        translator = Translator()
        traduzioni = {}
        for desc in descrizioni:
            try:
                tradotto = translator.translate(desc, src='en', dest='it').text
                traduzioni[desc] = tradotto
            except Exception as e:
                print(f"Errore nella traduzione di '{desc}': {e}")
                traduzioni[desc] = desc

        dati_fittizi = []
        for data in df['data'].sort_values():
            temp = round(random.choice(temperature) + random.uniform(-1.5, 1.5), 1)
            umidita = round(random.choice(umidita_values) + random.uniform(-5, 5), 1)
            precipitazioni = round(random.choice(precipitazioni_values) + random.uniform(-0.5, 0.5), 2)
            precipitazioni = max(0, precipitazioni)

            descrizione_en = random.choice(descrizioni)
            descrizione_it = traduzioni.get(descrizione_en, descrizione_en)

            dati_fittizi.append({
                "data": data.strftime("%Y-%m-%d"),
                "temp": f"{temp}°C",
                "descrizione": descrizione_it,
                "umidita": f"{umidita}%",
                "precipitazioni": f"{precipitazioni} mm"
            })

        df_fittizi = pd.DataFrame(dati_fittizi)
        df_fittizi.to_csv(file_output, index=False)

        print(f"File '{file_output}' generato con successo.")

    except Exception as e:
        print(f"Errore nella generazione dei dati fittizi: {e}")


def crea_database_meteo():
    print("Creando database solo con dati fittizi...")

    try:
        # Assicurati che le cartelle esistano
        os.makedirs('meteo', exist_ok=True)
        os.makedirs('database', exist_ok=True)

        file_fittizio = os.path.join('meteo', "dati_fittizi_meteo.csv")
        db_file = os.path.join('database', 'meteo.db')

        # Verifica che il file CSV esista
        if not os.path.exists(file_fittizio):
            print(f"File '{file_fittizio}' non trovato.")
            return

        # Elimina il database esistente se c'è
        if os.path.exists(db_file):
            os.remove(db_file)
            print(f"Database '{db_file}' esistente eliminato.")

        # Caricamento e pulizia dei dati dal CSV
        df_fittizio = pd.read_csv(file_fittizio, parse_dates=["data"])
        df_fittizio['temp'] = df_fittizio['temp'].str.replace("°C", "").astype(float)
        df_fittizio['umidita'] = df_fittizio['umidita'].str.replace("%", "").astype(float)
        df_fittizio['precipitazioni'] = df_fittizio['precipitazioni'].str.replace(" mm", "").astype(float)

        df_fittizio = df_fittizio.dropna(subset=['temp', 'descrizione', 'umidita', 'precipitazioni'])

        # Connessione e creazione tabella
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        c.execute('''
            CREATE TABLE meteo_fittizio (
                data DATE,
                temp REAL,
                descrizione TEXT,
                umidita REAL,
                precipitazioni REAL
            )
        ''')

        # Inserimento dati nel database
        for index, row in df_fittizio.iterrows():
            try:
                c.execute('''
                    INSERT INTO meteo_fittizio (data, temp, descrizione, umidita, precipitazioni) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    row['data'].strftime("%Y-%m-%d"),
                    float(row['temp']),
                    str(row['descrizione']),
                    float(row['umidita']),
                    float(row['precipitazioni'])
                ))
            except Exception as e:
                print(f"Errore inserendo i dati per {row['data']}: {e}")
                continue

        conn.commit()
        conn.close()
        print("Database creato e popolato correttamente!")

    except Exception as e:
        print(f"Errore nella creazione del database: {e}")

def esporta_database_meteo():
    print("Esportazione dei dati dal database al file 'meteo_fittizio.txt'...")

    try:
        db_file = os.path.join('database', 'meteo.db')
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        c.execute('SELECT * FROM meteo_fittizio')
        rows = c.fetchall()

        if not rows:
            print("Nessun dato da esportare.")
            return

        file_txt = os.path.join('database', 'meteo_fittizio.txt')

        with open(file_txt, 'w', encoding='utf-8') as f:
            f.write("Data\tTemperatura\tDescrizione\tUmidità\tPrecipitazioni\n")
            for row in rows:
                data = row[0]
                temp = f"{row[1]}°C"
                descrizione = row[2]
                umidita = f"{row[3]}%"
                precipitazioni = f"{row[4]} mm"
                f.write(f"{data}\t{temp}\t{descrizione}\t{umidita}\t{precipitazioni}\n")

        print(f"Esportazione completata con successo in {file_txt}.")

        conn.close()

    except Exception as e:
        print(f"Errore durante l'esportazione: {e}")

def crea_dati_fittizi_ortaggi():
    print("Generando dati fittizi...")

    df_reale = pd.read_csv('produzione/ortaggi_completo.csv')

    def genera_valore_fittizio(valore_reale):
        if pd.isna(valore_reale):
            return valore_reale
        
        if valore_reale == 0:
            return round(random.uniform(0.05, 0.1), 2)
        
        variazione = random.uniform(-0.05, 0.05)
        valore_fittizio = round(valore_reale * (1 + variazione), 2)
        return max(valore_fittizio, 0)

    oggi = datetime.today()
    mese_corrente = oggi.month
    anno_corrente = oggi.year

    colonne_mesi = [col for col in df_reale.columns if '-' in col and col not in ['Note']]

    ultima_colonna = colonne_mesi[-1] if colonne_mesi else None

    for idx, row in df_reale.iterrows():
        for col in df_reale.columns:
            if col in ['Stagione', 'Ortaggio', 'Valuta/UM', 'Semina', 'Trapianto', 'Raccolta', 'Note', 'PRODUZIONE 2024 in mgl']:
                continue
            valore_reale = row[col]
            valore_fittizio = genera_valore_fittizio(valore_reale)
            df_reale.at[idx, col] = valore_fittizio

    if ultima_colonna:
        anno_ultimo, mese_ultimo = map(int, ultima_colonna.split('-'))

        if (mese_corrente == 1 and mese_ultimo == 12 and anno_corrente - anno_ultimo == 1) or \
           (mese_corrente > 1 and mese_ultimo == mese_corrente - 1 and anno_corrente == anno_ultimo):
            print(f"Il mese precedente ({ultima_colonna}) è presente nel file.")
        else:
            mese_precedente = f"{anno_corrente}-{str(mese_corrente - 1).zfill(2)}"
            print(f"Il mese precedente ({mese_precedente}) non è presente. Aggiungo il mese {mese_precedente}.")
            posizione_produzione = df_reale.columns.get_loc('PRODUZIONE 2024 in mgl')
            df_reale.insert(posizione_produzione, mese_precedente, None)

            for idx, row in df_reale.iterrows():
                valore_reale = row.get('2024-03', 0)
                valore_fittizio = genera_valore_fittizio(valore_reale)
                df_reale.at[idx, mese_precedente] = valore_fittizio

    ultimo_giorno = oggi.replace(day=28) + pd.Timedelta(days=4)
    ultimo_giorno = ultimo_giorno - pd.Timedelta(days=ultimo_giorno.day)

    if oggi.date() == ultimo_giorno.date():
        print(f"Oggi è l’ultimo giorno del mese ({oggi.date()}). Aggiungo il mese corrente.")
        mese_da_aggiungere = f"{anno_corrente}-{str(mese_corrente).zfill(2)}"

        if mese_da_aggiungere not in df_reale.columns:
            posizione_produzione = df_reale.columns.get_loc('PRODUZIONE 2024 in mgl')
            df_reale.insert(posizione_produzione, mese_da_aggiungere, None)

        mese_2024 = f"2024-{str(mese_corrente).zfill(2)}"
        if mese_2024 in df_reale.columns:
            for idx, row in df_reale.iterrows():
                valore_reale = row[mese_2024]
                nuovo_valore = genera_valore_fittizio(valore_reale)
                df_reale.at[idx, mese_da_aggiungere] = nuovo_valore

    else:
        print(f"Oggi non è l’ultimo giorno del mese ({oggi.date()}), aggiorno solo i dati esistenti.")

    file_path = 'produzione/ortaggi_completo_fittizio.csv'
    if os.path.exists(file_path):
        os.remove(file_path)

    df_reale.to_csv(file_path, index=False, encoding='utf-8')
    print("File 'ortaggi_completo_fittizio.csv' aggiornato.")



def crea_database_ortaggi():
    # Crea la cartella 'database' se non esiste
    os.makedirs('database', exist_ok=True)

    # Crea la cartella 'produzione' se non esiste
    os.makedirs('produzione', exist_ok=True)

    db_file = os.path.join('database', 'ortaggi.db')

    # Elimina il database esistente per ricrearlo da zero
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Database esistente eliminato.")

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    file_csv = os.path.join('produzione', 'ortaggi_completo_fittizio.csv')

    try:
        with open(file_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            colonne_mesi = [colonna for colonna in header if '-' in colonna]

            query_creazione = '''CREATE TABLE IF NOT EXISTS ortaggi (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    stagione TEXT,
                                    nome TEXT,
                                    valuta TEXT,
                                 '''

            for colonna in colonne_mesi:
                query_creazione += f'"{colonna}" REAL, '

            query_creazione += '''produzione_2024 REAL,
                                  semina TEXT,
                                  trapianto TEXT,
                                  raccolta TEXT,
                                  note TEXT)'''

            c.execute(query_creazione)

            dati_inseriti = False

            for row in reader:
                if len(row) < len(header):
                    row += ["valore inesistente"] * (len(header) - len(row))

                stagione, nome, valuta = row[0], row[1], row[2]

                c.execute('SELECT 1 FROM ortaggi WHERE nome = ? AND valuta = ? LIMIT 1', (nome, valuta))
                if c.fetchone() is None:
                    query_inserimento = f'''INSERT INTO ortaggi (
                                            stagione, nome, valuta, {", ".join(f'"{col}"' for col in colonne_mesi)},
                                            produzione_2024, semina, trapianto, raccolta, note)
                                            VALUES ({", ".join(["?"] * (3 + len(colonne_mesi) + 5))})'''
                    c.execute(query_inserimento, [stagione, nome, valuta] + row[3:])
                    dati_inseriti = True

            conn.commit()

            if dati_inseriti:
                print("Dati inseriti con successo nel database!")
            else:
                print("Ci sono già tutti i dati all'interno del database.")

    except FileNotFoundError:
        print(f"Errore: il file CSV {file_csv} non è stato trovato.")
    except Exception as e:
        print(f"Errore durante l'inserimento nel database: {e}")
    finally:
        conn.close()


def esporta_database_ortaggi():
    db_file = os.path.join('database', 'ortaggi.db')
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute("SELECT * FROM ortaggi")
    
    righe = c.fetchall()

    file_txt = os.path.join('database', 'database_ortaggi.txt')

    try:
        with open(file_txt, 'w') as f:
            col_names = [desc[0] for desc in c.description]
            f.write("\t".join(col_names) + "\n")
            
            for riga in righe:
                f.write("\t".join(map(str, riga)) + "\n")
        
        print(f"Dati esportati con successo in {file_txt}")

    except Exception as e:
        print(f"Errore durante l'esportazione dei dati: {e}")

    finally:
        conn.close()

def crea_database_utenti():
    try:
        if not os.path.exists('database'):
            os.makedirs('database')
        
        db_path = os.path.join('database', 'users.db')
        
        if not os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            c = conn.cursor()

            c.execute('''
                CREATE TABLE utenti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')

            c.execute('''
                INSERT INTO utenti (username, password) VALUES (?, ?)
            ''', ('admin', 'admin'))

            conn.commit()
            conn.close()
            print(f"Database utenti creato con utente admin/admin nella cartella 'database'.")
        else:
            print("ℹDatabase utenti già esistente nella cartella 'database'.")
    
    except sqlite3.Error as e:
        print(f"Errore durante la creazione del database: {e}")


def esporta_database_utenti():
    db_path = 'database/users.db'
    output_path = 'database/users.txt'
    
    if not os.path.exists('database'):
        os.makedirs('database')
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute('SELECT * FROM utenti')
    utenti = c.fetchall()
    
    with open(output_path, 'w') as file:
        file.write('ID\tUsername\tPassword\n')
        
        for utente in utenti:
            file.write(f"{utente[0]}\t{utente[1]}\t{utente[2]}\n")
    
    conn.close()

# Funzione principale
if __name__ == "__main__":
    print("Avvio creazione completa dei dati...")

    scarica_dati_meteo()
    crea_dati_fittizi_meteo()
    crea_database_meteo()
    #esporta_database_meteo()
    crea_dati_fittizi_ortaggi()
    crea_database_ortaggi()
    #esporta_database_ortaggi()
    crea_database_utenti()
    #esporta_database_utenti()

    print("Tutto aggiornato con successo!")