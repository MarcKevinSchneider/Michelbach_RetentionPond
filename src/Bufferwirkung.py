# Skript: Berechnung der Bufferwirkung des Rückhaltebeckens
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

path = "/data/"
path_plots = "/plots/"

messungen = pd.read_csv(f"{path}/Nitrat_Phosphat/Nitrat_Phosphat.csv")

# kopie
df = messungen.copy()

# codatum zu datetime
df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

# größer und kleiner zeichen weg und zu float
for col in ["Nitrat", "Phosphor"]:
    df[col] = (
        df[col].astype(str)
        .replace({r"<0\.5": "0.5", r">5\.0": "5.0"}, regex=True)
        .astype(float)
    )

# wieder average
df_avg = (
    df
    .groupby(["Datum", df["Probe"].str[:2]]) 
    .agg({"Nitrat": "mean", "Phosphor": "mean", "NPOC": "mean"})
    .reset_index()
    .rename(columns={"Probe": "Ort"})
)

# zu wide format 
df_wide = df_avg.pivot(index="Datum", columns="Ort", values=["Nitrat", "Phosphor", "NPOC"])
df_wide.columns = ['_'.join(col) for col in df_wide.columns]  # flatten multiindex
df_wide.reset_index(inplace=True)

# differenz zwischen den messpunkten
df_wide['Nitrat_diff'] = df_wide['Nitrat_AP'] - df_wide['Nitrat_SP']
df_wide['Phosphor_diff'] = df_wide['Phosphor_AP'] - df_wide['Phosphor_SP']
df_wide['NPOC_diff'] = df_wide['NPOC_AP'] - df_wide['NPOC_SP']

# dann differenz in prozent
df_wide['Nitrat_pct'] = (df_wide['Nitrat_AP'] - df_wide['Nitrat_SP']) / df_wide['Nitrat_AP'] * 100
df_wide['Phosphor_pct'] = (df_wide['Phosphor_AP'] - df_wide['Phosphor_SP']) / df_wide['Phosphor_AP'] * 100
df_wide['NPOC_pct'] = (df_wide['NPOC_AP'] - df_wide['NPOC_SP']) / df_wide['NPOC_AP'] * 100

# differenz in prozent über zeit
plt.figure(figsize=(10,5))
plt.plot(df_wide['Datum'], df_wide['Nitrat_pct'], label='Nitrat', marker='o')
plt.plot(df_wide['Datum'], df_wide['Phosphor_pct'], label='Phosphor', marker='o')
plt.plot(df_wide['Datum'], df_wide['NPOC_pct'], label='NPOC', marker='o')
plt.axhline(0, color='k', linestyle='--')
plt.ylabel("Percent Reduction (%)")
plt.xlabel("Date")
plt.title("Pond Buffer Effect on Nutrients")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# long format
df_long = df_wide.melt(
    id_vars="Datum",
    value_vars=["Nitrat_pct", "Phosphor_pct", "NPOC_pct"],
    var_name="Nutrient",
    value_name="Percent_Reduction"
)

# umbenennen der spalten fürs plotting
df_long['Nutrient'] = df_long['Nutrient'].replace({
    "Nitrat_pct": "Nitrate",
    "Phosphor_pct": "Orthophosphate",
    "NPOC_pct": "NPOC"
})

# boxplot der differenzen
plt.figure(figsize=(12,8))
sns.boxplot(data=df_long, x="Nutrient", y="Percent_Reduction", palette="Set2")
sns.stripplot(data=df_long, x="Nutrient", y="Percent_Reduction", color="black", alpha=0.5, jitter=True)
plt.axhline(0, color='k', linestyle='--')
plt.ylabel("Percent Reduction (%)")
plt.grid(True, linestyle="--", alpha=0.6)
#plt.title("Pond Buffer Effect on Nutrients")
plt.savefig(f"{path_plots}/Bufferwirkung_Boxplot.png", 
            dpi=300)
plt.show()