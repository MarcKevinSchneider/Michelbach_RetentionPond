# Skript: Formatierung der Uniwald Caldern Grubenwiese Station
# Autor: Marc Kevin Schneider
# Datum: September 2025

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

path = "/data/"
path_plots = "/plots/"

# stündliche stationsdaten
station_hourly = pd.read_csv(f"{path}/Hourly_Wiese_Klimastation.csv")
station_hourly["datetime"] = pd.to_datetime(station_hourly["datetime"])
station_hourly = station_hourly.loc[(station_hourly["datetime"] >= "2025-05-10") & (station_hourly["datetime"] <= "2025-07-20")]

# tägliche stationsdaten
station_daily = pd.read_csv(f"{path}/Daily_Wiese_Klimastation.csv")
station_daily["datetime"] = pd.to_datetime(station_daily["datetime"])
station_daily = station_daily.loc[(station_daily["datetime"] >= "2025-05-10") & (station_daily["datetime"] <= "2025-07-20")]


# ein plot drei subplots
fig, axes = plt.subplots(3, 1, figsize=(14, 12), sharex=True)

# erster plot luft temperatur und luftfeuchte auf 2m höhe
axes[0].plot(station_hourly["datetime"], station_hourly["Ta_2m"], color="red", label="2m Air Temperature [°C]", alpha=0.7)
axes[0].set_ylabel("Air Temperature [°C]", color="red")
axes[0].tick_params(axis="y", labelcolor="red")
axes[0].set_ylim(-5, 40)
axes[0].grid(True, linestyle="--", alpha=0.5)

# twin achse für relative luftfeuchte
ax2 = axes[0].twinx()
ax2.plot(station_hourly["datetime"], station_hourly["Huma_2m"], color="blue", label="2m Relative Humidity (%)", alpha=0.7)
ax2.set_ylabel("Relative Humidity [%]", color="blue")
ax2.tick_params(axis="y", labelcolor="blue")
axes[0].set_title("A) Hourly Air Temperature and Relative Humidity")
axes[0].legend(loc="upper left")
ax2.legend(loc="upper right")
ax2.set_ylim(25, 110)

# stündliche net radiation
axes[1].plot(station_hourly["datetime"], station_hourly["rad_net"], color="orange")
axes[1].set_ylabel("Net Radiation [W/m²]")
axes[1].set_title("B) Hourly Net Radiation")

# täglicher niederschlag
axes[2].bar(station_daily["datetime"], station_daily["PCP"], color="skyblue")
axes[2].set_ylabel("Daily Precipitation [mm]")
axes[2].set_xlabel("Date")
axes[2].set_title("C) Daily Precipitation")

for ax in axes:
    ax.set_xlim(pd.to_datetime("2025-05-10"), pd.to_datetime("2025-07-20"))

plt.tight_layout()
plt.savefig(f"{path_plots}/Übersicht_Station_Grubenwiese.png", 
            dpi=300)
plt.show()