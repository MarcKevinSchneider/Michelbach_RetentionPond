# Skript: Auswertung der Nitrat, Orthophosphat und NPOC Werte
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats
from scipy.stats import spearmanr, pearsonr, shapiro

path = "/data/"
path_plots = "/plots/"

messungen = pd.read_csv(f"{path}/Nitrat_Phosphat/Nitrat_Phosphat.csv")

# kopie
df = messungen.copy()

# datum zu datetime
df["Datum"] = pd.to_datetime(df["Datum"], format="%d.%m.%Y")

# größer und kleiner zeichen weg und zu float
for col in ["Nitrat", "Phosphor"]:
    df[col] = (
        df[col].astype(str)
        .replace({r"<0\.5": "0.5", r">5\.0": "5.0"}, regex=True)
        .astype(float)
    )


# plot mit drei subplots
fig, axes = plt.subplots(3, 1, figsize=(12,8), sharex=True)

# nitrat als erster subplot
sns.lineplot(
    data=df, x="Datum", y="Nitrat", hue="Probe", marker="o", ax=axes[0]
)
axes[0].set_title("A) Nitrate Concentration")
axes[0].set_ylabel("Nitrate [mg/L]")
axes[0].set_xlabel("") # keine x-achsen beschriftung hier da wir sharex=True gesetzt haben, axes[2] macht damit die labels
axes[0].legend(title="Probe")

# phosphor als zweiter plot
sns.lineplot(
    data=df, x="Datum", y="Phosphor", hue="Probe", marker="o", ax=axes[1]
)
axes[1].set_title("B) Orthophosphate Concentration")
axes[1].set_ylabel("Orthophosphate [mg/L]")
axes[1].set_xlabel("")
axes[1].legend(title="Probe")

sns.lineplot(
    data=df, x="Datum", y="NPOC", hue="Probe", marker="o", ax=axes[2]
)
axes[2].set_title("B) NPOC Concentration")
axes[2].set_ylabel("NPOC [mg/L]")
axes[2].set_xlabel("Date")
axes[2].legend(title="Probe")

plt.tight_layout()
plt.savefig(f"{path_plots}/Nitrat_Phosphat_NPOC_Zeitserie.png", 
            dpi=300)
plt.show()


###############################################################

# durchschnitt über proben
df_avg = (
    df
    .groupby(["Datum", df["Probe"].str[:2]]) 
    .agg({"Nitrat": "mean", "Phosphor": "mean", "NPOC": "mean"})
    .reset_index()
    .rename(columns={"Probe": "Ort"})
)


# gleicher plot wie oben, nur mit den averaged daten
fig, axes = plt.subplots(2, 1, figsize=(12,8), sharex=True)

# Nitrat (top)
sns.lineplot(
    data=df_avg, x="Datum", y="Nitrat", hue="Ort", marker="o", ax=axes[0]
)
axes[0].set_title("A) Nitrate Concentration")
axes[0].set_ylabel("Nitrate [mg/L]")
axes[0].set_xlabel("")
axes[0].legend(title="Ort")

# Phosphor (unten)
sns.lineplot(
    data=df_avg, x="Datum", y="Phosphor", hue="Ort", marker="o", ax=axes[1]
)
axes[1].set_title("B) Orthophosphate Concentration ")
axes[1].set_ylabel("Orthophosphate [mg/L]")
axes[1].set_xlabel("Date")
axes[1].legend(title="Ort")

plt.tight_layout()
plt.savefig(f"{path_plots}/Durchschnitt_Nitrat_Phosphat_Zeitserie.png", 
            dpi=300)
plt.show()


#########################################################

# korrelation zwischen den umweltparametern und der nitrat-/phosphatkonzentration
# korrelationsmatrix

# durchschnitt jetzt auch für die umweltparameter
env_cols = ["Datum", "Probe", "Temp", "LF", "PPM", "pH"]
env_avg = (
    messungen[env_cols]
    .copy()
    .groupby(["Datum", messungen["Probe"].str[:2]])  
    .mean(numeric_only=True)
    .reset_index()
    .rename(columns={"Probe": "Ort"})
)

# beide dfs zu datetime
df_avg["Datum"] = pd.to_datetime(df_avg["Datum"])
env_avg["Datum"] = pd.to_datetime(env_avg["Datum"], format="%d.%m.%Y")

# dann mergen
df_avg_full = pd.merge(df_avg, env_avg, on=["Datum", "Ort"], how="left")

# filter für die spalten die uns interessieren
cols = ["Nitrat", "Phosphor", "NPOC", "Temp", "LF", "PPM", "pH"]
data = df_avg_full[cols]

# shapiro wilk test um auf normalverteilung zu testen
normality_results = {}
for col in cols:
    # alle NaN raus
    stat, p = shapiro(data[col].dropna())
    normality_results[col] = p
    print(f"{col}: Shapiro-Wilk p = {p:.4f}")

# nv wennn p > 0.05
if all(pval > 0.05 for pval in normality_results.values()):
    method = "pearson"
    print("NV ==> Pearson correlation.")
else:
    method = "spearman"
    print("Nicht NV ==> Spearman correlation.")

# wählt die vom Shapiro-Wilk Test ausgewählte methode für die korrelationsanalyse
corr = data.corr(method=method)

# p-werte händisch
pvals = pd.DataFrame(np.ones((len(cols), len(cols))), index=cols, columns=cols)
# müssen wir pairwise die NAs droppen damit die p-werte am ende nicht alle NaN sind
for i in range(len(cols)):
    for j in range(len(cols)):
        if i != j:
            # schmeiß reihen wo irgendeiner der werte NA ist raus
            x = data.iloc[:, i]
            y = data.iloc[:, j]
            valid = x.notna() & y.notna()
            if valid.sum() > 1:  # mindestens 2 punkte
                # wählt dann den vorher gewählten korrelationskoeffizienten aus
                if method == "pearson":
                    pvals.iloc[i, j] = pearsonr(x[valid], y[valid])[1]
                else:
                    pvals.iloc[i, j] = spearmanr(x[valid], y[valid])[1]

# das ist nur dazu da um die obere rechte ecke bei der heatmap auszumaskieren
mask = np.triu(np.ones_like(corr, dtype=bool))

# heatmap plot
plt.figure(figsize=(8, 6))
ax = sns.heatmap(
    corr,
    mask=mask,
    annot=True,
    cmap="coolwarm",
    center=0,
    linewidths=0.5,
    cbar_kws={"shrink": 0.8},
    vmin = -1, 
    vmax= 1
)

# statistisch signifikante ergebnisse mit dickem rand
for i in range(len(cols)):
    for j in range(len(cols)):
        if not mask[i, j] and pvals.iloc[i, j] < 0.05:
            ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=False, edgecolor="black", lw=2))

#plt.title("Nitrate and Orthophosphate Correlation Matrix")
plt.savefig(f"{path_plots}/Korrelationsmatrix_Nitrat_Phosphat_NPOC.png", 
            dpi=300)
plt.show()



###################################################################################

# korrelation der nitrat und phosphat werte mit den wetterstationsdaten uniwald caldern
# mit lags (positiv und negativ) um auch zeitversetzte effekte zu identifizieren

# stationsdaten lesen (Wetterstation Uniwiese Caldern)
station = pd.read_csv(f"{path}/Hourly_Wiese_Klimastation.csv")
# datetime
station["datetime"] = pd.to_datetime(station["datetime"])

# daten sind momentan stündlich, hier resamplen wir zu täglich damit das mit den messwerten des rückhaltebeckens übereinstimmt
station_daily = (
    station.resample("1d", on="datetime")
        .agg({
            # summe für niederschlag
            "PCP": "sum", 
            # mean für alles andere
            **{col: "mean" for col in station.columns if col not in ["datetime", "PCP"]}
        }).round(3))

# index resetten damit datetime wieder als spalte zurückkommt
station_daily = station_daily.reset_index(drop=False)

# erstmal saven
station_daily.to_csv(f"{path}/Daily_Wiese_Klimastation.csv", 
                     index=False)

# daten nur für den untersuchungszeitraum
station_daily = station_daily.loc[(station_daily["datetime"] >= "2025-05-10") & (station_daily["datetime"] <= "2025-07-31")]


# variablen die mit einander korreliert werden sollen
pond_vars = ["Nitrat", "Phosphor", "NPOC", "Temp", "LF", "PPM", "pH"]
weather_vars = ["Ta_2m", "PCP"]

# lags in tagen (von 0 bis 14, sowohl positiv als auch negativ)
lags = [-14, -7, -3, -2, -1, 0, 1, 2, 3, 7, 14]

# leeres dataframes für die ergebnisse
# eins für die korrelationen
corrs = {wvar: pd.DataFrame(index=pond_vars, columns=lags, dtype=float) for wvar in weather_vars}
# eins für die p-werte
pvals = {wvar: pd.DataFrame(index=pond_vars, columns=lags, dtype=float) for wvar in weather_vars}

# loop für alle lags
for lag in lags:
    station_shifted = station_daily.copy()
    # packt den lag auf die daten drauf
    station_shifted["datetime_shifted"] = station_shifted["datetime"] + pd.Timedelta(days=lag)
    
    # merged die dataframes dann 
    merged = pd.merge(
        df_avg_full,
        station_shifted[["datetime_shifted"] + weather_vars],
        left_on="Datum",
        right_on="datetime_shifted",
        how="left"
    )
    
    # berechnet für jede variable dann die spearmans rho korrelation und die p-werte
    for var in pond_vars:
        for wvar in weather_vars:
            valid = merged[[var, wvar]].dropna()
            if len(valid) > 1:
                rho, pval = spearmanr(valid[var], valid[wvar])
                corrs[wvar].loc[var, lag] = rho
                pvals[wvar].loc[var, lag] = pval

# ein plot mit zwei subplots
fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# heatmap für lufttemperatur (Ta_2m) und niederschlag (PCP)
for ax, wvar in zip(axes, weather_vars):
    sns.heatmap(corrs[wvar], annot=True, cmap="coolwarm", center=0, 
                cbar_kws={"label": f"Spearman rho"}, ax=ax, vmin=-1, vmax=1)
    
    # dicke umrandung falls statistisch signifikant
    for i in range(corrs[wvar].shape[0]):
        for j in range(corrs[wvar].shape[1]):
            if pvals[wvar].iloc[i, j] is not np.nan and pvals[wvar].iloc[i, j] < 0.05:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, fill=False, edgecolor='black', lw=3))
    
# labels
axes[0].set_ylabel("Pond variable")
axes[1].set_ylabel("Pond variable")
axes[1].set_xlabel("Lags (in days)")
axes[0].set_title(f"A) Air Temperature")
axes[1].set_title(f"B) Precipitation")
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(f"{path_plots}/Lag_Analyse_Ta2m_PCP_TeichVariablen.png", 
            dpi=300)
plt.show()