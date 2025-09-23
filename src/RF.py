# Skript: Auswertung der Shimadzu RF-6000 Daten
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from glob import glob
from Funktionen import read_shimadzu_file, plot_fluorescence_heatmap, plot_location_over_time

path = "/data/"
path_plots = "/plots/"

ap = glob(f"{path}/RF/AP*.txt")

sp = glob(f"{path}/RF/SP*.txt")

for f in ap:
    # ID und datum aus dem Dateinamen
    fname = f.split("\\")[-1].replace(".txt", "")
    
    df = read_shimadzu_file(f)
    df.to_csv(f"{path}/RF/{fname}.csv", index=False)

for f in sp:
    # ID und datum aus dem Dateinamen
    fname = f.split("\\")[-1].replace(".txt", "")
    
    df = read_shimadzu_file(f)
    df.to_csv(f"{path}/RF/{fname}.csv", index=False)

###############################################################################

# alle zusammen

# pfade für alle .csv dateien
all_files = glob(f"{path}/RF/*.csv")

# leere liste für alle daten
combined_data = []

for f in all_files:
    # probennamen und datum extrahieren
    fname = f.split("\\")[-1].replace(".csv", "")
    series, date_str = fname.split("_")
    # datum wieder zu datetime
    sample_date = pd.to_datetime(date_str, format="%d%m%y")
    
    # lese .csv
    df = pd.read_csv(f)
    # packe probennamen und datum dazu
    df["Series"] = series
    df["Sample_Date"] = sample_date
    
    combined_data.append(df)

# aneinanderpacken fürs dataframe
all_df = pd.concat(combined_data, ignore_index=True)

# überflüssige spalte löschen
all_df = all_df.drop("Unnamed: 177", axis=1)

# speichern
all_df.to_csv(f"{path}/RF/RF6000_AlleProben.csv", index=False)


###########################################################################

# visualisierung

# daten lesen
all_df = pd.read_csv(f"{path}/RF/RF6000_AlleProben.csv")
all_df["Sample_Date"] = pd.to_datetime(all_df["Sample_Date"])

# heatmap plotten
plot_fluorescence_heatmap(all_df, series="AP01", sample_date="2025-07-01", vmax=200, vmin=0)

# alle Proben und Beprobungspunkte plotten
for series in all_df["Series"].unique():
    for date in all_df["Sample_Date"].unique():
        try:
            plot_fluorescence_heatmap(all_df, series=series, sample_date=date, vmax=200, vmin=0)
            print(f"Completed {series} on {date}...")
        except ValueError:
            continue


# nur location als spalte, damit wir die Proben zusammenrechnen können
all_df["Location"] = all_df["Series"].str[:2]

# numerische Spalten
em_cols = [c for c in all_df.columns if c not in ["EX Wavelength/EM Wavelength", "Series", "Sample_Date", "Location"]]

# gruppieren für location + datum + wellenlänge und dann average (z.B. AP01 und AP02 am 15.06. durchschnitt)
mean_df = (
    all_df.groupby(["Location", "Sample_Date", "EX Wavelength/EM Wavelength"], as_index=False)[em_cols]
          .mean()
)

# nochmal speichern
mean_df.to_csv(f"{path}/RF/Durchschnitt_RF6000_AlleProben.csv", index=False)


mean_df = pd.read_csv(f"{path}/RF/Durchschnitt_RF6000_AlleProben.csv")
mean_df["Sample_Date"] = pd.to_datetime(mean_df["Sample_Date"])

# zeitserie für die heatmaps
plot_location_over_time(mean_df, location="AP", vmax=200, vmin=0)