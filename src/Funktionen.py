# Skript: Funktionen für die anderen Skripte
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

path_plots = "/plots/"


def plot_absorbed_radiation(df):
    """
    Sinn: Plottet die absorbierte Strahlung der Proben über Zeit

    Parameter:
    ----------------------------------

    df : pd.DataFrame
        Dataframe der Daten

        
    Ergebnis:
    ----------------------------------
    Plot der absorbierten Strahlung
    """
    # konvertiert absorption zu absorbierter Strahlung in %
    df["PercentAbsorbed"] = (1 - 10 ** (-df["Absorbance"])) * 100

    # checkt nochmal die Sortierung
    df = df.sort_values(by=["Date", "Wavelength_nm"])

    # erstellt figure
    plt.figure(figsize=(10, 6))

    # gruppieren + plotten aller samples
    for (date, sample), group in df.groupby(["Date", "Sample"]):
        plt.plot(
            group["Wavelength_nm"],
            group["PercentAbsorbed"],
            label=f"{sample} ({date})"
        )

    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Absorbed Radiation (%)")
    plt.title("Percentage of Radiation Absorbed in Samples")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_absorbed_radiation_ax(df, ax, title):
    """
    Sinn: Plottet die absorbierte Strahlung der Proben über Zeit

    Parameter:
    ----------------------------------

    df : pd.DataFrame
        Dataframe der Daten

        
    Ergebnis:
    ----------------------------------
    Plot der absorbierten Strahlung
    """
    # konvertiert absorption zu absorbierter Strahlung in %
    df["PercentAbsorbed"] = (1 - 10 ** (-df["Absorbance"])) * 100

    # checkt nochmal die Sortierung
    df = df.sort_values(by=["Date", "Wavelength_nm"])


    # gruppieren + plotten aller samples
    for (date, sample), group in df.groupby(["Date", "Location"]):
        ax.plot(
            group["Wavelength_nm"],
            group["PercentAbsorbed"],
            label=f"{sample} ({date})"
        )

    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Absorbed Radiation (%)")
    ax.set_title(f"{title}")
    ax.legend()
    ax.grid(True)



def read_shimadzu_file(file_path):
    """
    Sinn: Liest die Daten des Shimadzu RF6000 Fluorospectrometer und macht daraus eine .csv Datei

    Parameter:
    ---------------------------------------

    file_path: str
        Pfad zur Datei

    Ergebnis:
    ---------------------------------------
    .csv Datei der vorherigen .txt-Datei

    """
    # ließt die anzahl an lines in der datei
    with open(file_path, "r") as f:
        lines = f.readlines()

    # finde die header datei
    for i, line in enumerate(lines):
        if line.startswith('"EX Wavelength/EM Wavelength"'):
            header_line_index = i
            break
    else:
        raise ValueError(f"Keine Spaltennamendaten gefunden in: {file_path}")

    # extrahiere header
    header = [h.replace('"', '') for h in lines[header_line_index].strip().split(",")]
    n_cols = len(header)

    # extrahiere die numerischen daten
    data_lines = lines[header_line_index + 1:]
    data = []
    for line in data_lines:
        if line.strip():
            values = [x for x in line.strip().split(",") if x != '']
            # NaN wenn eine Zeile weniger Werte als Header hat
            if len(values) < n_cols:
                values += [float('nan')] * (n_cols - len(values))
            # beschneide Zeile sie mehr Werte als der Header hat
            elif len(values) > n_cols:
                values = values[:n_cols]
            # konvertiere alle zu float
            data.append([float(x) for x in values])

    df = pd.DataFrame(data, columns=header)
    return df

def plot_fluorescence_heatmap(df, series, sample_date, vmax=None, vmin=None, figsize=(12,6)):
    """
    Sinn: Plotted eine 2D Fluoresenz heatmap für eine Probe und Datum
    
    Parameter:
    -------------------------------------
        df : pandas.DataFrame
            DataFrame mit allen Proben

        series : str
            Probenname (z.B.: "AP01", "SP01")

        sample_date : str oder datetime
            Beprobungsdatum

        vmax : float, optional
            Maximalwert für die colorscale

        vmin : float, optional
            Minimalwert für die colorscale

        figsize : tuple, optional
            Größe des Plots

            
    Ergebnis:
    -------------------------------------
    Heatmap, die ähnlich dem Display des Shimidzu RF-6000 ist
    """
    # konvertiere zu Datetime falls notwendig
    sample_date = pd.to_datetime(sample_date)
    
    # probe auswählen
    sample_df = df[(df["Series"] == series) & (df["Sample_Date"] == sample_date)]
    if sample_df.empty:
        raise ValueError(f"Keine Daten für Probe {series} am {sample_date.date()}")
    
    # numerische spalten identifizieren
    em_cols = [c for c in sample_df.columns 
               if c not in ["EX Wavelength/EM Wavelength", "Series", "Sample_Date"] 
               and not str(c).startswith("Unnamed")]
    
    # spaltennamen zu float
    em_values = np.array([float(c) for c in em_cols])
    
    # intensitätsmatrix extrahieren
    intensity_matrix = sample_df[em_cols].values
    
    # EX Wellenlängen
    ex_values = sample_df["EX Wavelength/EM Wavelength"].values
    
    # Tick abstand fürs plotting
    x_tick_step = max(len(em_values) // 10, 1)
    y_tick_step = max(len(ex_values) // 10, 1)
    
    # tick labels mit dem abstand von oben
    xtick_labels = [f"{v:.0f}" if i % x_tick_step == 0 else "" for i, v in enumerate(em_values)]
    ytick_labels = [f"{v:.0f}" if i % y_tick_step == 0 else "" for i, v in enumerate(ex_values)]
    
    # heatmap
    plt.figure(figsize=figsize)
    sns.heatmap(intensity_matrix, 
                xticklabels=xtick_labels, 
                yticklabels=ytick_labels, 
                cmap="viridis",
                vmax=vmax,
                vmin=vmin)
    
    plt.xlabel("EM Wavelength [nm]")
    plt.ylabel("EX Wavelength [nm]")
    plt.title(f"Fluorescence 2D spectrum ({series} {sample_date.date()})")
    sample_date = str(sample_date)[0:9]
    plt.savefig(f"{path_plots}/RF_{series}_{sample_date}.png",
                dpi=300)
    plt.show()



def plot_location_over_time(df, location, vmax=None, vmin=None, figsize=(16,8)):
    """
    Sinn: Plotted 2D Fluoreszenz Heatmaps über die gesamte Zeitserie
    
    Parameter:
    -------------------------------------
        df : pandas.DataFrame
            DataFrame mit allen Proben

        location: str
            Name des Probenortes; möglich sind "AP" und "SP"

        vmax: float
            Max. Wert der Colorscale; optional; standardmäßig auf "None" gesetzt

        vmin: float
            Min. Wert der Colorscale; optional; standardmäßig auf "None" gesetzt

        figsize : tuple, optional
            Größe des Plots

            
    Ergebnis:
    -------------------------------------
    Heatmaps, die ähnlich dem Display des Shimidzu RF-6000 sind, aber über die Zeitreihe
    """
    # sortieren nach Aufnahmedatum
    dates = sorted(df.loc[df["Location"] == location, "Sample_Date"].unique())
    n = len(dates)
    # Anzahl der Subplots in Abhängigkeit von der Anzahl an Messpunkten
    fig, axes = plt.subplots(1, n, figsize=figsize, sharey=True)
    
    # falls es nur ein Messdatum gibt
    if n == 1:  
        axes = [axes]
    
    # sonst loop
    for i, date in enumerate(dates):
        # extrahiere Daten
        sample_df = df[(df["Location"] == location) & (df["Sample_Date"] == date)]
        
        # extrahiere Spalten
        em_cols = [c for c in sample_df.columns if c not in ["EX Wavelength/EM Wavelength", "Sample_Date", "Location"]]
        # erst zu float dann zu array
        em_values = np.array([float(c) for c in em_cols])
        ex_values = sample_df["EX Wavelength/EM Wavelength"].values
        # als Matrix extrahieren
        intensity_matrix = sample_df[em_cols].values
        
        # für die x- und y-Achsenbeschriftungen
        # macht alle 10 Schritte eine Beschriftung
        x_tick_step = max(len(em_values) // 10, 1)
        y_tick_step = max(len(ex_values) // 10, 1)
        xtick_labels = [f"{v:.0f}" if j % x_tick_step == 0 else "" for j, v in enumerate(em_values)]
        ytick_labels = [f"{v:.0f}" if j % y_tick_step == 0 else "" for j, v in enumerate(ex_values)]
        
        # plotte heatmap
        sns.heatmap(intensity_matrix,
                    cmap="viridis", 
                    vmax=vmax, vmin=vmin,
                    xticklabels=xtick_labels,
                    yticklabels=ytick_labels,
                    ax=axes[i])
        
        # setzt das Datum als subplot titel
        axes[i].set_title(str(date.date()))
        axes[i].set_xlabel("EM Wavelength [nm]")
        if i == 0:
            axes[i].set_ylabel("EX Wavelength [nm]")
        else:
            axes[i].set_ylabel("")
    
    # weiteres formatting
    plt.suptitle(f"Fluorescence spectra over time – {location}", fontsize=16)
    plt.tight_layout()
    # speichern
    plt.savefig(f"{path_plots}/RF_{location}_Timeseries.png", dpi=300)
    plt.show()