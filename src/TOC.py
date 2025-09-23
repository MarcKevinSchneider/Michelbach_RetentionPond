# Skript: Auswertung der TOC-L Daten
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt

path = "/data/"
path_plots = "/plots/"


# .txt datei lesen (hab davor alle Werte, die nicht zu uns gehören einfach rausgelöscht)
toc = pd.read_csv(f"{path}/TOC/2025_09_23.txt", sep=",")

# alle unnötigen Spalten löschen
toc = toc.drop(["Typ", "Unnamed: 19", "ProbenID", "Original", 
                "Kal.Kurve", "Anmerk.", "Analyse(Inj.)"], axis=1)

# sortieren
toc = toc.sort_values(by=["Probenname"],ascending=True).reset_index(drop=True)

# alle mit 0 in der Spalte Standardabweichung löschen (sind eh fehlerhaft)
toc_filter = toc[toc["Std. Abw. Konz"] != 0]

# alle doppelten Werte auch rauslöschen (behalte aber den ersten Wert aller Dopplungen, sonst löscht man alles lol)
toc_filter = toc_filter.drop_duplicates(subset=["Std. Abw. Konz"], keep="first").reset_index(drop=True)

# nerviges "NPOC:" vor dem eigentlichen Ergebnis entfernen
toc_filter["Ergebnis"] = toc_filter["Ergebnis"].str.replace("NPOC:", "", regex=False)

# lösche noch Zeile 17 da die Daten nicht in Ordnung aussehen
toc_filter = toc_filter.drop(17, axis=0)

# speichern
toc_filter.to_csv(f"{path}/TOC/TOC_250923.csv", index=False)


#########################################################

# visualisierung

toc_filter = pd.read_csv(f"{path}/TOC/TOC_250923.csv")

# lösche fürs plotting die einheit raus
toc_filter["Ergebnis_Wert"] = (
    toc_filter["Ergebnis"]
    .str.replace("mg/L", "", regex=False)
    .astype(float)
)

# extrahiere den probennamen
toc_filter["Datum"] = toc_filter["Probenname"].str.extract(r"_(\d{6})")[0]
# zu datetime (dann kann man das als x-achse benutzen)
toc_filter["Datum"] = pd.to_datetime(toc_filter["Datum"], format="%d%m%y")

# extrahiere den gruppennamen der proben (also z.B. ap01, ap02, usw.)
toc_filter["Gruppe"] = toc_filter["Probenname"].str.extract(r"(^[A-Z]+\d+)")[0]

# initialisiere plot
plt.figure(figsize=(12, 6))

# plotte jeden wert in jeder gruppe und verbinde als liniengraphen
for series, group in toc_filter.groupby("Gruppe"):
    group_sorted = group.sort_values("Datum")
    plt.plot(group_sorted["Datum"], group_sorted["Ergebnis_Wert"], marker="o", label=series)

# für die achsenbeschriftungen usw. 
plt.xlabel("Sample Date")
plt.ylabel("Concentration [mg/L]")
plt.title("NPOC values over time")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
