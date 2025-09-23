# Skript: Auswertung der UV/Vis Spectrometer Daten
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from Funktionen import plot_absorbed_radiation, plot_absorbed_radiation_ax
import seaborn as sns

path = "/data/"
path_plots = "/plots/"

ap = glob(f"{path}/UVVIS/AP*.csv")

sp = glob(f"{path}/UVVIS/SP*.csv")

###########################################################################################

# für alle AP messungen 
all_data = []

for f in ap:
    # ID und datum aus dem Dateinamen
    fname = f.split("\\")[-1].replace(".csv", "")
    sample_id, date_str = fname.split("_")
    
    # zu datetime
    date_formatted = pd.to_datetime(date_str, format="%d%m%y").date()
    
    # absorptionsdaten lesen + header skippen (info brauchen wir nicht)
    df = pd.read_csv(f, sep=";", skiprows=2, names=["Wavelength_nm", "Absorbance"], decimal=",")
    
    # infos zur messung dazu
    df["Date"] = date_formatted
    df["Sample"] = sample_id
    
    all_data.append(df)

# zu einem df
combined = pd.concat(all_data, ignore_index=True)

# hier sortieren wir noch nach dem Datum damit die ältesten Proben ganz oben sind
# + wir sortieren auch nach der Wellenlänge
combined = combined.sort_values(
    by=["Date", "Wavelength_nm"],
    ascending=[True, True]
).reset_index(drop=True)

# speichern
combined.to_csv(f"{path}/UVVIS/AP_Messungen.csv", index=False)


####################################################################################################

# für alle SP messungen 
all_data = []

for f in sp: #dateinamen nur von AP zu SP geändert, code klappt dann so trotzdem
    # ID und datum aus dem Dateinamen
    fname = f.split("\\")[-1].replace(".csv", "")
    sample_id, date_str = fname.split("_")
    
    # zu datetime
    date_formatted = pd.to_datetime(date_str, format="%d%m%y").date()
    
    # absorptionsdaten lesen + header skippen (info brauchen wir nicht)
    df = pd.read_csv(f, sep=";", skiprows=2, names=["Wavelength_nm", "Absorbance"], decimal=",")
    
    # infos zur messung dazu
    df["Date"] = date_formatted
    df["Sample"] = sample_id
    
    all_data.append(df)

# zu einem df
combined = pd.concat(all_data, ignore_index=True)

# hier sortieren wir noch nach dem Datum damit die ältesten Proben ganz oben sind
# + wir sortieren auch nach der Wellenlänge
combined = combined.sort_values(
    by=["Date", "Wavelength_nm"],
    ascending=[True, True]
).reset_index(drop=True)

# speichern (namen natürlich auch hier ändern)
combined.to_csv(f"{path}/UVVIS/SP_Messungen.csv", index=False)


####################################################################################################################

# visualisierung

# daten wieder einlesen
ap_messungen = pd.read_csv(f"{path}/UVVIS/AP_Messungen.csv")
sp_messungen = pd.read_csv(f"{path}/UVVIS/SP_Messungen.csv")

plot_absorbed_radiation(ap_messungen)
plot_absorbed_radiation(sp_messungen)


# date datetime
ap_messungen["Date"] = pd.to_datetime(ap_messungen["Date"])
sp_messungen["Date"] = pd.to_datetime(sp_messungen["Date"])

# nur AP oder SP (Zahl weglassen)
ap_messungen["Location"] = ap_messungen["Sample"].str[:2]
sp_messungen["Location"] = sp_messungen["Sample"].str[:2]

#gruppieren für location, date, wavelength und dann durchschnitt
ap_mean = (
    ap_messungen.groupby(["Location", "Date", "Wavelength_nm"], as_index=False)[["Absorbance", "PercentAbsorbed"]]
    .mean()
)

sp_mean = (
    sp_messungen.groupby(["Location", "Date", "Wavelength_nm"], as_index=False)[["Absorbance", "PercentAbsorbed"]]
    .mean()
)

ap_mean.to_csv(f"{path}/UVVIS/Durchschnitt_AP_Messungen.csv", index=False)
sp_mean.to_csv(f"{path}/UVVIS/Durchschnitt_SP_Messungen.csv", index=False)

#############################################################################

ap_mean = pd.read_csv(f"{path}/UVVIS/Durchschnitt_AP_Messungen.csv")
sp_mean = pd.read_csv(f"{path}/UVVIS/Durchschnitt_SP_Messungen.csv")

fig, axes = plt.subplots(1, 2, figsize=(16,8))
plot_absorbed_radiation_ax(ap_mean, axes[0], "A) AP Samples")
plot_absorbed_radiation_ax(sp_mean, axes[1], "B) SP Samples")
plt.tight_layout()
plt.savefig(f"{path_plots}/UVVIS_AP_SP_Durchschnitt.png", 
            dpi=300)
plt.show()


##############################################

# korrelationsanalyse

# erstmal die beiden datensätze mergen
merged = pd.merge(
    ap_mean,
    sp_mean,
    on=["Date", "Wavelength_nm"],
    suffixes=("_AP", "_SP"), # packt an die daten die endungen dran, damit man die auseinander halten kann
    how="inner" # schmeißt einzeltermine raus, z.B. wenn SP Daten hat und AP nicht
)

# korrelation über alle messpunkte hinweg
# erstmal für absorption
corr_abs = merged["Absorbance_AP"].corr(merged["Absorbance_SP"])
# und für prozent absorbierte strahlung
corr_pct = merged["PercentAbsorbed_AP"].corr(merged["PercentAbsorbed_SP"])

print("Korrelation Absorption:", corr_abs)
print("Korrelation Prozent absorbiert:", corr_pct)


# korrelation für jedes Datum
date_corrs = (
    merged.groupby("Date")
          .apply(lambda g: pd.Series({
              "Absorbance_corr": g["Absorbance_AP"].corr(g["Absorbance_SP"]),
              "PercentAbsorbed_corr": g["PercentAbsorbed_AP"].corr(g["PercentAbsorbed_SP"])
          }))
)

print(date_corrs)


# beziehung AP und SP Werte

# schmeißen NA raus
merged_valid = merged.dropna(subset=["Absorbance_AP", "Absorbance_SP"])

# r2 
r = merged_valid["Absorbance_AP"].corr(merged_valid["Absorbance_SP"])
r2 = r**2

# scatterplot mit regressionslinie
plt.figure(figsize=(8,6))
sns.regplot(
    data=merged_valid,
    x="Absorbance_AP", 
    y="Absorbance_SP",
    scatter_kws={"s": 10, "alpha": 0.5},
    line_kws={"color": "red"}
)

plt.xlabel("AP Absorbance [a.u.]")
plt.ylabel("SP Absorbance [a.u.]")
plt.title("Relationship AP and SP absorbance")

# r2 im plot anmerken
plt.text(
    0.05, 0.95, 
    f"$R^2$ = {r2:.3f}", 
    ha="left", va="top", transform=plt.gca().transAxes,
    fontsize=12, bbox=dict(facecolor="white", alpha=0.7, edgecolor="none")
)

plt.tight_layout()
plt.savefig(f"{path_plots}/UVVIS_AP_SP_Beziehung.png", 
            dpi=300)
plt.show()
