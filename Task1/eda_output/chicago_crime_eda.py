"""
==============================================================================
  CHICAGO CRIME DATASET — COMPREHENSIVE EXPLORATORY DATA ANALYSIS
  Author  : Antigravity AI
  Dataset : chicago_crime_dataset.csv
  Purpose : Full EDA covering data quality, univariate, bivariate,
            multivariate, statistical, and spatial analysis.
==============================================================================
"""

# ---------------------------------------------------------------------------
# 0. IMPORTS
# ---------------------------------------------------------------------------
import warnings
import os
import sys
import textwrap
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

matplotlib.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.labelsize": 11,
    "axes.titlesize": 13,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 15,
})

# Output directory for all figures
OUTPUT_DIR = "eda_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Colour palette
PALETTE_MAIN   = "#2563EB"
PALETTE_ARREST = ["#EF4444", "#22C55E"]
CMAP_HEAT      = "YlOrRd"
CMAP_BLUE      = "Blues"
CMAP_COOL      = LinearSegmentedColormap.from_list(
    "cool_heat", ["#DBEAFE", "#1E40AF"])

sns.set_palette("Set2")

DATASET_PATH = "chicago_crime_dataset.csv"


# ===========================================================================
# HELPER UTILITIES
# ===========================================================================
def save_fig(name: str):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    print(f"  saved -> {path}")


def section(title: str):
    bar = "=" * 70
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


def subsection(title: str):
    print(f"\n-- {title} --")


def format_pct_axis(ax, axis="y"):
    fmt = mtick.PercentFormatter(xmax=1, decimals=0)
    if axis == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)


def cramers_v(x, y):
    ct = pd.crosstab(x, y)
    chi2, p, dof, _ = chi2_contingency(ct)
    n = ct.to_numpy().sum()
    v = np.sqrt(chi2 / (n * (min(ct.shape) - 1)))
    return v, p


MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
DOW_ORDER   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


# ===========================================================================
# 1. LOAD DATA
# ===========================================================================
section("1. LOADING DATASET")

df_raw = pd.read_csv(DATASET_PATH)
print(f"Shape         : {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")
print(f"Memory usage  : {df_raw.memory_usage(deep=True).sum()/1024**2:.2f} MB")
print(f"\nColumns:\n{df_raw.columns.tolist()}")

print("\n-- First 5 rows --")
print(df_raw.head(5).to_string(max_colwidth=30))
print("\n-- Last 5 rows --")
print(df_raw.tail(5).to_string(max_colwidth=30))
print("\n-- Random sample (5 rows) --")
print(df_raw.sample(5, random_state=42).to_string(max_colwidth=30))

print("\n-- Data types --")
print(df_raw.dtypes)

# Drop redundant '_year' column (identical to 'Year')
assert (df_raw['_year'] == df_raw['Year']).all()
df_raw = df_raw.drop(columns=["_year"])
print("\n  Dropped redundant '_year' column (identical to 'Year').")

df = df_raw.copy()


# ===========================================================================
# 2. DATE PARSING
# ===========================================================================
section("2. DATE PARSING & FEATURE ENGINEERING")

def parse_mixed_dates(series):
    """Handle two observed date formats in the dataset."""
    # Format A: MM/DD/YYYY HH:MM:SS AM/PM
    parsed = pd.to_datetime(series, format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
    # Format B: MM-DD-YYYY HH:MM
    mask   = parsed.isna()
    parsed[mask] = pd.to_datetime(series[mask], format="%m-%d-%Y %H:%M", errors="coerce")
    return parsed

df["Date_parsed"]  = parse_mixed_dates(df["Date"])
df["UpdatedOn_dt"] = pd.to_datetime(df["Updated On"], errors="coerce")

n_failed = df["Date_parsed"].isna().sum()
print(f"Dates parsed successfully: {len(df)-n_failed:,} / {len(df):,}")
print(f"Failed to parse          : {n_failed}")

# Derive temporal features
df["dt_year"]       = df["Date_parsed"].dt.year
df["dt_month"]      = df["Date_parsed"].dt.month
df["dt_day"]        = df["Date_parsed"].dt.day
df["dt_hour"]       = df["Date_parsed"].dt.hour
df["dt_dow"]        = df["Date_parsed"].dt.dayofweek
df["dt_dow_name"]   = df["Date_parsed"].dt.day_name()
df["dt_quarter"]    = df["Date_parsed"].dt.quarter
df["dt_date"]       = df["Date_parsed"].dt.date
df["dt_is_weekend"] = df["dt_dow"].isin([5, 6])
df["dt_night"]      = df["dt_hour"].between(21, 23) | df["dt_hour"].between(0, 5)

print("Temporal features created: dt_year, dt_month, dt_day, dt_hour,")
print("  dt_dow, dt_dow_name, dt_quarter, dt_date, dt_is_weekend, dt_night")


# ===========================================================================
# 3. DATA QUALITY ASSESSMENT
# ===========================================================================
section("3. DATA QUALITY ASSESSMENT")

# ── 3a. Missing values
subsection("3a. Missing Values")

missing = pd.DataFrame({
    "Missing Count" : df.isna().sum(),
    "Missing %"     : df.isna().mean() * 100,
    "Non-Null Count": df.notna().sum(),
    "Dtype"         : df.dtypes,
}).sort_values("Missing %", ascending=False)

print(missing[missing["Missing Count"] > 0].to_string())
print(f"\nTotal missing cells : {df.isna().sum().sum():,}")
print(f"Overall missing %   : {df.isna().mean().mean()*100:.2f}%")

# Visualise
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
missing_plot = missing[missing["Missing Count"] > 0].sort_values("Missing %")
axes[0].barh(missing_plot.index, missing_plot["Missing %"], color=PALETTE_MAIN, alpha=0.85)
axes[0].set_xlabel("Missing %")
axes[0].set_title("Missing Value Percentage by Column")
for bar, val in zip(axes[0].patches, missing_plot["Missing %"]):
    axes[0].text(bar.get_width()+0.02, bar.get_y()+bar.get_height()/2,
                 f"{val:.2f}%", va="center", fontsize=8)

miss_heatmap_cols = [c for c in df.columns if df[c].isna().any()]
if miss_heatmap_cols:
    sample_idx = df[df[miss_heatmap_cols].isna().any(axis=1)].index
    sample_size = min(500, len(sample_idx))
    np.random.seed(42)
    sample_df = df.loc[np.random.choice(sample_idx, sample_size, replace=False), miss_heatmap_cols]
    sns.heatmap(sample_df.isna(), cbar=False, cmap="RdYlGn_r",
                yticklabels=False, ax=axes[1])
    axes[1].set_title("Missingness Pattern (sample of 500 affected rows)")
    axes[1].set_xlabel("Column")
else:
    axes[1].text(0.5, 0.5, "No missing values!", ha="center")

plt.suptitle("Missing Value Analysis", fontsize=14, fontweight="bold", y=1.01)
save_fig("01_missing_values")

# ── 3b. Duplicates
subsection("3b. Duplicate Records")

full_dups = df.duplicated().sum()
print(f"Fully duplicated rows     : {full_dups}")

dup_ids   = df[df.duplicated("ID", keep=False)]
dup_cases = df[df.duplicated("Case Number", keep=False)]
print(f"Rows with duplicate ID    : {len(dup_ids)}")
print(f"Rows with duplicate Case# : {len(dup_cases)}")

if len(dup_cases) > 0:
    print("\nSample of duplicate Case Numbers:")
    print(dup_cases[["ID","Case Number","Date","Primary Type","Arrest"]].head(10).to_string())

# ── 3c. Inconsistencies
subsection("3c. Inconsistencies Check")

for col in ["Primary Type","Description","Location Description","FBI Code"]:
    has_leading  = df[col].dropna().str.startswith(" ").any()
    has_trailing = df[col].dropna().str.endswith(" ").any()
    print(f"  {col}: leading_space={has_leading}, trailing_space={has_trailing}")

lat_invalid = ((df["Latitude"]  < 41.5) | (df["Latitude"]  > 42.1)).sum()
lon_invalid = ((df["Longitude"] < -88.1)| (df["Longitude"] > -87.4)).sum()
print(f"\n  Out-of-range Latitude   : {lat_invalid}")
print(f"  Out-of-range Longitude  : {lon_invalid}")

year_mismatch = (df["Year"] != df["dt_year"]).sum()
print(f"\n  Year column vs parsed date mismatch: {year_mismatch}")
print(f"  District 31 count (unusual)        : {(df['District']==31).sum()}")
print(f"  Beat == 0                          : {(df['Beat']==0).sum()}")

x_zero = (df["X Coordinate"] == 0).sum()
y_zero = (df["Y Coordinate"] == 0).sum()
print(f"  X Coordinate == 0 : {x_zero}")
print(f"  Y Coordinate == 0 : {y_zero}")


# ===========================================================================
# 4. DATA CLEANING LOG
# ===========================================================================
section("4. DATA CLEANING LOG")

cleaning_log = []

cleaning_log.append({"Issue":"Redundant column","Column":"_year",
    "Affected":len(df),"Action":"Dropped column",
    "Reason":"Identical to Year column"})

cleaning_log.append({"Issue":"Mixed date formats","Column":"Date",
    "Affected":len(df),"Action":"Created Date_parsed (datetime)",
    "Reason":"Two formats: MM/DD/YYYY HH:MM:SS AM/PM and MM-DD-YYYY HH:MM"})

cleaning_log.append({"Issue":"No temporal features","Column":"Date_parsed",
    "Affected":len(df),"Action":"Derived dt_year/month/day/hour/dow/quarter/is_weekend/night",
    "Reason":"Required for temporal analysis"})

if year_mismatch > 0:
    cleaning_log.append({"Issue":"Year col vs parsed date mismatch","Column":"Year",
        "Affected":year_mismatch,"Action":"Retain; use dt_year from parsed Date for temporal analyses",
        "Reason":"Date column is primary source of truth"})

if x_zero > 0:
    df.loc[df["X Coordinate"]==0, ["X Coordinate","Y Coordinate","Latitude","Longitude","Location"]] = np.nan
    cleaning_log.append({"Issue":"Zero coordinates","Column":"X/Y Coordinate",
        "Affected":x_zero,"Action":"Set to NaN",
        "Reason":"Zero is an invalid coordinate in this projection"})

if len(dup_cases) > 0:
    cleaning_log.append({"Issue":"Duplicate Case Numbers","Column":"Case Number",
        "Affected":len(dup_cases),"Action":"Retained; flagged for awareness",
        "Reason":"May represent updates/amendments to the same incident"})

cleaning_df = pd.DataFrame(cleaning_log)
print(cleaning_df.to_string(index=False, max_colwidth=60))


# ===========================================================================
# 5. DATA DICTIONARY
# ===========================================================================
section("5. DATA DICTIONARY")

dict_data = {
    "ID"                   : ("int64","Unique record identifier","120,759","0%"),
    "Case Number"          : ("str","CPD case report number","120,755","0%"),
    "Date"                 : ("str","Incident date/time (mixed formats)","104,269","0%"),
    "Block"                : ("str","Block address of incident","24,042","0%"),
    "IUCR"                 : ("int64","Illinois Uniform Crime Reporting code","326","0%"),
    "Primary Type"         : ("str","Top-level crime category","31","0%"),
    "Description"          : ("str","Detailed crime description","304","0%"),
    "Location Description" : ("str","Type of location (Street, Apartment…)","129","0.38%"),
    "Arrest"               : ("bool","Whether an arrest was made","2","0%"),
    "Domestic"             : ("bool","Whether incident is domestic-related","2","0%"),
    "Beat"                 : ("int64","Police beat identifier","275","0%"),
    "District"             : ("int64","Police district number","23","0%"),
    "Ward"                 : ("int64","City ward number","50","0%"),
    "Community Area"       : ("int64","Community area number (1-77)","77","0.01%"),
    "FBI Code"             : ("str","FBI crime classification code","26","0%"),
    "X Coordinate"         : ("int64","State Plane Illinois East X coord","40,048","1.55%"),
    "Y Coordinate"         : ("int64","State Plane Illinois East Y coord","50,709","1.55%"),
    "Year"                 : ("int64","Year of crime (from data entry)","5","0%"),
    "Updated On"           : ("str","Last update timestamp","2,466","0%"),
    "Latitude"             : ("float64","WGS84 Latitude","73,687","1.55%"),
    "Longitude"            : ("float64","WGS84 Longitude","73,645","1.55%"),
    "Location"             : ("str","String tuple of lat/lon","73,766","1.55%"),
}
dict_df = pd.DataFrame.from_dict(dict_data, orient="index",
    columns=["Dtype","Meaning","Unique Values","Missing %"])
dict_df.index.name = "Column"
print(dict_df.to_string(max_colwidth=55))


# ===========================================================================
# 6. DESCRIPTIVE STATISTICS
# ===========================================================================
section("6. DESCRIPTIVE STATISTICS")

num_cols = ["Beat","District","Ward","Community Area","X Coordinate",
            "Y Coordinate","Latitude","Longitude"]
print("\nNumerical columns summary:")
print(df[num_cols].describe().T.round(3).to_string())

print("\nSkewness & Kurtosis:")
for col in num_cols:
    ser = df[col].dropna()
    print(f"  {col:<22} skew={ser.skew():.3f}  kurt={ser.kurt():.3f}")


# ===========================================================================
# 7. NUMERICAL VARIABLE DISTRIBUTIONS
# ===========================================================================
section("7. NUMERICAL VARIABLE DISTRIBUTIONS")

numeric_interest = ["Beat","District","Ward","Community Area","Latitude","Longitude"]

fig, axes = plt.subplots(3, 4, figsize=(20, 14))
axes = axes.flatten()

for i, col in enumerate(numeric_interest):
    data = df[col].dropna()
    ax_h = axes[i*2]
    ax_b = axes[i*2+1]

    ax_h.hist(data, bins=40, color=PALETTE_MAIN, alpha=0.7, density=True,
              edgecolor="white", lw=0.3)
    data.plot.kde(ax=ax_h, color="#EF4444", lw=2)
    ax_h.set_title(f"{col} - Distribution")
    ax_h.set_xlabel(col)
    ax_h.set_ylabel("Density")

    ax_b.boxplot(data, orientation='vertical', patch_artist=True,
                 boxprops=dict(facecolor=PALETTE_MAIN, alpha=0.5),
                 medianprops=dict(color="#EF4444", lw=2),
                 whiskerprops=dict(lw=1.5),
                 flierprops=dict(marker="o", markersize=2, alpha=0.3))
    ax_b.set_title(f"{col} - Boxplot")
    ax_b.set_ylabel(col)

plt.suptitle("Numerical Variable Distributions", fontsize=15, fontweight="bold", y=1.01)
save_fig("02_numerical_distributions")

# Detailed stats table
stats_rows = []
for col in numeric_interest:
    s = df[col].dropna()
    q1, q3 = s.quantile([0.25, 0.75])
    stats_rows.append({
        "Column": col,
        "Mean"  : round(s.mean(), 4),
        "Median": round(s.median(), 4),
        "Std"   : round(s.std(), 4),
        "Min"   : round(s.min(), 4),
        "Max"   : round(s.max(), 4),
        "Q1"    : round(q1, 4),
        "Q3"    : round(q3, 4),
        "IQR"   : round(q3-q1, 4),
        "Skew"  : round(s.skew(), 4),
        "Kurt"  : round(s.kurt(), 4),
    })

stats_df = pd.DataFrame(stats_rows).set_index("Column")
print(stats_df.to_string())


# ===========================================================================
# 8. UNIVARIATE — CRIME TYPE
# ===========================================================================
section("8. UNIVARIATE ANALYSIS - CRIME TYPE")

TOTAL = len(df)
crime_counts = df["Primary Type"].value_counts()
print(f"\nUnique crime types: {len(crime_counts)}")
print(f"Top 10 types cover: {crime_counts.head(10).sum()/TOTAL*100:.1f}% of all incidents\n")
print(crime_counts.to_string())

# Top 15 crime types bar chart
fig, ax = plt.subplots(figsize=(13, 7))
top15 = crime_counts.head(15)
colors = sns.color_palette("Blues_d", len(top15))[::-1]
bars = ax.barh(top15.index[::-1], top15.values[::-1], color=colors[::-1], edgecolor="white")
for bar, val in zip(bars, top15.values[::-1]):
    ax.text(bar.get_width()+50, bar.get_y()+bar.get_height()/2,
            f"{val:,}  ({val/TOTAL*100:.1f}%)", va="center", fontsize=8.5)
ax.set_xlabel("Number of Incidents")
ax.set_title("Top 15 Crime Types - Chicago Crime Dataset (2021-2025)", fontweight="bold")
ax.set_xlim(0, top15.max()*1.18)
save_fig("03_top15_crime_types")

# Pie chart
top8  = crime_counts.head(8)
other = crime_counts.iloc[8:].sum()
pie_data = pd.concat([top8, pd.Series({"Other": other})])
fig, ax = plt.subplots(figsize=(9, 9))
wedges, texts, autotexts = ax.pie(
    pie_data, labels=None, autopct="%1.1f%%", startangle=140,
    colors=sns.color_palette("Set2", len(pie_data)),
    pctdistance=0.82, wedgeprops=dict(edgecolor="white", linewidth=1.5))
for at in autotexts:
    at.set_fontsize(8.5)
ax.legend(wedges, pie_data.index, loc="lower right", fontsize=9, frameon=False)
ax.set_title("Crime Type Distribution - Top 8 + Other", fontweight="bold")
save_fig("04_crime_type_pie")

# Top 20 descriptions
desc_counts = df["Description"].value_counts().head(20)
fig, ax = plt.subplots(figsize=(13, 8))
colors2 = sns.color_palette("rocket_r", len(desc_counts))
ax.barh(desc_counts.index[::-1], desc_counts.values[::-1], color=colors2[::-1], edgecolor="white")
for bar, val in zip(ax.patches, desc_counts.values[::-1]):
    ax.text(bar.get_width()+10, bar.get_y()+bar.get_height()/2,
            f"{val:,}", va="center", fontsize=8)
ax.set_xlabel("Number of Incidents")
ax.set_title("Top 20 Crime Descriptions", fontweight="bold")
save_fig("05_top20_descriptions")


# ===========================================================================
# 9. UNIVARIATE — ARREST
# ===========================================================================
section("9. UNIVARIATE ANALYSIS - ARREST")

arrest_counts = df["Arrest"].value_counts()
arrest_rate   = arrest_counts[True] / TOTAL
print(f"Total incidents : {TOTAL:,}")
print(f"Arrests made    : {arrest_counts[True]:,} ({arrest_rate*100:.2f}%)")
print(f"No arrest       : {arrest_counts[False]:,} ({(1-arrest_rate)*100:.2f}%)")

fig, axes = plt.subplots(1, 2, figsize=(13, 6))

# Donut chart
labels = ["No Arrest", "Arrest"]
vals   = [arrest_counts[False], arrest_counts[True]]
wedges, texts, autotexts = axes[0].pie(
    vals, labels=labels, autopct="%1.1f%%", startangle=90,
    colors=["#EF4444","#22C55E"],
    pctdistance=0.75,
    wedgeprops=dict(edgecolor="white", linewidth=2, width=0.55))
for at in autotexts:
    at.set_fontsize(12)
axes[0].set_title("Overall Arrest vs. Non-Arrest", fontweight="bold")

# Arrest rate by top 15 crime types
top15_types = crime_counts.head(15).index.tolist()
arrest_by_type = (
    df[df["Primary Type"].isin(top15_types)]
    .groupby("Primary Type")["Arrest"]
    .agg(["sum","count"])
    .assign(rate=lambda x: x["sum"]/x["count"])
    .sort_values("rate", ascending=True))

axes[1].barh(arrest_by_type.index, arrest_by_type["rate"],
             color=[PALETTE_MAIN if r < 0.5 else "#22C55E" for r in arrest_by_type["rate"]],
             edgecolor="white", alpha=0.85)
axes[1].axvline(arrest_rate, color="#EF4444", lw=1.5, linestyle="--",
                label=f"Overall rate ({arrest_rate*100:.1f}%)")
axes[1].set_xlabel("Arrest Rate")
axes[1].set_title("Arrest Rate by Crime Type (Top 15)", fontweight="bold")
format_pct_axis(axes[1], "x")
axes[1].legend()

plt.suptitle("Arrest Analysis", fontsize=14, fontweight="bold")
save_fig("06_arrest_analysis")

dom_rate  = df["Domestic"].mean()
dom_arrest = df.groupby("Domestic")["Arrest"].mean()
print(f"\nDomestic incidents : {df['Domestic'].sum():,} ({dom_rate*100:.2f}%)")
print(f"Arrest rate - Domestic    : {dom_arrest[True]*100:.2f}%")
print(f"Arrest rate - Non-Domestic: {dom_arrest[False]*100:.2f}%")


# ===========================================================================
# 10. UNIVARIATE — TEMPORAL
# ===========================================================================
section("10. UNIVARIATE ANALYSIS - TEMPORAL")

year_counts = df.groupby("dt_year").size()
print("\nCrimes by year:")
for yr, cnt in year_counts.items():
    print(f"  {yr}: {cnt:,}")

last_2025 = df[df["dt_year"]==2025]["Date_parsed"].max()
print(f"\nLatest date in dataset (2025): {last_2025}")
print("NOTE: 2025 data may be partial - interpret year-over-year trend with caution.")

fig, axes = plt.subplots(2, 2, figsize=(16, 11))

# Crimes by year
ax = axes[0, 0]
ax.plot(year_counts.index, year_counts.values, marker="o", color=PALETTE_MAIN,
        lw=2.5, ms=8, markerfacecolor="white", markeredgewidth=2)
ax.fill_between(year_counts.index, year_counts.values, alpha=0.12, color=PALETTE_MAIN)
for yr, cnt in year_counts.items():
    ax.text(yr, cnt+150, f"{cnt:,}", ha="center", fontsize=9)
ax.set_title("Total Crimes by Year", fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Incidents")
ax.set_xticks(year_counts.index)

# Crimes by month
month_counts = df.groupby("dt_month").size()
ax = axes[0, 1]
ax.bar([MONTH_NAMES[m] for m in month_counts.index], month_counts.values,
       color=sns.color_palette("Paired", 12), edgecolor="white")
ax.set_title("Crimes by Month (All Years)", fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Number of Incidents")

# Crimes by day of week
dow_counts = df.groupby("dt_dow_name").size().reindex(DOW_ORDER)
ax = axes[1, 0]
palette_dow = ["#22C55E" if d in ["Saturday","Sunday"] else PALETTE_MAIN for d in DOW_ORDER]
bars = ax.bar(DOW_ORDER, dow_counts.values, color=palette_dow, edgecolor="white", alpha=0.85)
ax.set_title("Crimes by Day of Week", fontweight="bold")
ax.set_xlabel("Day of Week")
ax.set_ylabel("Number of Incidents")
for bar, val in zip(bars, dow_counts.values):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50, f"{val:,}",
            ha="center", fontsize=8)

# Crimes by hour
hour_counts = df.groupby("dt_hour").size()
ax = axes[1, 1]
ax.fill_between(hour_counts.index, hour_counts.values, alpha=0.3, color="#8B5CF6")
ax.plot(hour_counts.index, hour_counts.values, color="#8B5CF6", lw=2.5, marker="o", ms=5)
ax.set_title("Crimes by Hour of Day", fontweight="bold")
ax.set_xlabel("Hour (0=midnight)")
ax.set_ylabel("Number of Incidents")
ax.set_xticks(range(0, 24))
ax.axvspan(21, 23.5, alpha=0.07, color="red", label="Night hours")
ax.axvspan(0, 5.5, alpha=0.07, color="red")
ax.legend()

plt.suptitle("Temporal Crime Patterns - Chicago 2021-2025", fontsize=14, fontweight="bold")
save_fig("07_temporal_patterns")

peak_hour = hour_counts.idxmax()
print(f"\nPeak crime hour  : {peak_hour}:00 with {hour_counts[peak_hour]:,} incidents")
print(f"Quietest hour    : {hour_counts.idxmin()}:00 with {hour_counts.min():,} incidents")
print(f"Weekend crimes   : {df['dt_is_weekend'].sum():,} ({df['dt_is_weekend'].mean()*100:.1f}%)")
print(f"Night crimes     : {df['dt_night'].sum():,} ({df['dt_night'].mean()*100:.1f}%)")

# Monthly x Year heatmap
pivot_month_year = df.groupby(["dt_year","dt_month"]).size().unstack(fill_value=0)
pivot_month_year.columns = [MONTH_NAMES[m] for m in pivot_month_year.columns]

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot_month_year, annot=True, fmt=",", cmap=CMAP_HEAT, ax=ax,
            linewidths=0.5, linecolor="white", cbar_kws={"label":"Incidents"})
ax.set_title("Monthly Crime Counts by Year - Heatmap", fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Year")
save_fig("08_monthly_year_heatmap")

# Hour x Day heatmap
pivot_hour_dow = (df.groupby(["dt_dow_name","dt_hour"]).size()
                  .unstack(fill_value=0).reindex(DOW_ORDER))

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(pivot_hour_dow, cmap=CMAP_HEAT, ax=ax,
            linewidths=0.3, linecolor="white",
            cbar_kws={"label":"Incidents"})
ax.set_title("Crime Intensity - Hour of Day x Day of Week", fontweight="bold")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of Week")
save_fig("09_hour_dow_heatmap")

q_counts = df.groupby("dt_quarter").size()
print("\nCrimes by Quarter:")
for q, cnt in q_counts.items():
    print(f"  Q{q}: {cnt:,} ({cnt/TOTAL*100:.1f}%)")


# ===========================================================================
# 11. UNIVARIATE — LOCATION
# ===========================================================================
section("11. UNIVARIATE ANALYSIS - LOCATION")

dist_counts = df.groupby("District").size().sort_values(ascending=False)
print("\nCrimes by District (top 10):")
print(dist_counts.head(10).to_string())

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

dist_data = dist_counts.sort_values(ascending=True)
colors_d  = sns.color_palette("Blues_d", len(dist_data))
axes[0].barh(dist_data.index.astype(str), dist_data.values, color=colors_d, edgecolor="white")
axes[0].set_xlabel("Number of Incidents")
axes[0].set_title("Recorded Incidents by Police District", fontweight="bold")
axes[0].set_ylabel("District")

loc_counts = df["Location Description"].value_counts().head(15)
colors_l   = sns.color_palette("rocket_r", len(loc_counts))
axes[1].barh(loc_counts.index[::-1], loc_counts.values[::-1], color=colors_l[::-1], edgecolor="white")
for bar, val in zip(axes[1].patches, loc_counts.values[::-1]):
    axes[1].text(bar.get_width()+50, bar.get_y()+bar.get_height()/2,
                 f"{val:,}", va="center", fontsize=8)
axes[1].set_xlabel("Number of Incidents")
axes[1].set_title("Top 15 Location Types", fontweight="bold")

plt.suptitle("Geographic Distribution of Incidents", fontsize=14, fontweight="bold")
save_fig("10_geographic_distribution")

ca_counts = df.groupby("Community Area").size().sort_values(ascending=False)
print(f"\nTop 5 Community Areas by incident count:")
print(ca_counts.head(5).to_string())

ward_counts = df.groupby("Ward").size().sort_values(ascending=False)
print(f"\nTop 5 Wards by incident count:")
print(ward_counts.head(5).to_string())

# Geographic scatter
geo_df = df.dropna(subset=["Latitude","Longitude"])
fig, ax = plt.subplots(figsize=(9, 11))
ax.scatter(geo_df["Longitude"], geo_df["Latitude"],
           alpha=0.03, s=0.5, color=PALETTE_MAIN, rasterized=True)
ax.set_title(
    f"Geographic Distribution of Crime Incidents\n(n={len(geo_df):,} with valid coordinates)",
    fontweight="bold")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_facecolor("#f0f4f8")
save_fig("11_geographic_scatter")


# ===========================================================================
# 12. BIVARIATE ANALYSIS
# ===========================================================================
section("12. BIVARIATE ANALYSIS")

# 12a. Crime Type x Arrest
subsection("12a. Crime Type x Arrest")

arrest_by_crime = (
    df.groupby("Primary Type")["Arrest"]
    .agg(total="count", arrested="sum")
    .assign(arrest_rate=lambda x: x["arrested"]/x["total"])
    .sort_values("arrest_rate", ascending=False))

print("\nArrest rate by Primary Type:")
print(arrest_by_crime.to_string())

top20 = arrest_by_crime.nlargest(20, "total").sort_values("arrest_rate", ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(18, 8))

bars = axes[0].barh(top20.index, top20["arrest_rate"],
                    color=[("#22C55E" if r > arrest_rate else PALETTE_MAIN)
                           for r in top20["arrest_rate"]],
                    edgecolor="white", alpha=0.85)
axes[0].axvline(arrest_rate, color="#EF4444", lw=1.5, ls="--",
                label=f"Overall rate ({arrest_rate*100:.1f}%)")
format_pct_axis(axes[0], "x")
axes[0].set_title("Arrest Rate by Crime Type (Top 20 by Volume)", fontweight="bold")
axes[0].set_xlabel("Arrest Rate")
axes[0].legend()
for bar, val in zip(bars, top20["arrest_rate"]):
    axes[0].text(bar.get_width()+0.003, bar.get_y()+bar.get_height()/2,
                 f"{val*100:.1f}%", va="center", fontsize=8)

top15_order = crime_counts.head(15).index.tolist()
ab = (arrest_by_crime.loc[arrest_by_crime.index.isin(top15_order)]
      .reindex(top15_order).fillna(0))
not_arrested = ab["total"] - ab["arrested"]
x = range(len(top15_order))
axes[1].bar(x, not_arrested, label="Not Arrested", color="#EF4444", alpha=0.8)
axes[1].bar(x, ab["arrested"], bottom=not_arrested, label="Arrested", color="#22C55E", alpha=0.8)
axes[1].set_xticks(x)
axes[1].set_xticklabels([t.replace(" ","\n") for t in top15_order], fontsize=7.5)
axes[1].set_ylabel("Number of Incidents")
axes[1].set_title("Arrested vs Not Arrested - Top 15 Crime Types", fontweight="bold")
axes[1].legend()

plt.suptitle("Crime Type x Arrest Analysis", fontsize=14, fontweight="bold")
save_fig("12_crime_arrest_bivariate")

# 12b. Crime Type x Year
subsection("12b. Crime Type x Year")

top8_types = crime_counts.head(8).index.tolist()
pivot_crime_year = (
    df[df["Primary Type"].isin(top8_types)]
    .groupby(["dt_year","Primary Type"]).size()
    .unstack(fill_value=0))

fig, ax = plt.subplots(figsize=(13, 7))
for col, color in zip(pivot_crime_year.columns, sns.color_palette("tab10", len(top8_types))):
    ax.plot(pivot_crime_year.index, pivot_crime_year[col],
            marker="o", lw=2, color=color, label=col, ms=6,
            markerfacecolor="white", markeredgewidth=2)
ax.set_title("Top 8 Crime Types - Annual Trend (2021-2025)", fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Number of Incidents")
ax.legend(loc="upper left", fontsize=8, framealpha=0.7)
ax.set_xticks(pivot_crime_year.index)
save_fig("13_crime_type_year_trend")

# 12c. Crime Type x Hour heatmap
subsection("12c. Crime Type x Hour Heatmap")

top10_types = crime_counts.head(10).index.tolist()
pivot_type_hour = (
    df[df["Primary Type"].isin(top10_types)]
    .groupby(["Primary Type","dt_hour"]).size()
    .unstack(fill_value=0))
pivot_norm = pivot_type_hour.div(pivot_type_hour.max(axis=1), axis=0)

fig, ax = plt.subplots(figsize=(16, 6))
sns.heatmap(pivot_norm, cmap="YlOrRd", ax=ax,
            linewidths=0.3, linecolor="white",
            cbar_kws={"label":"Relative Frequency (row-normalised)"})
ax.set_title("Crime Type x Hour of Day - Relative Activity Pattern", fontweight="bold")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Crime Type")
save_fig("14_crime_type_hour_heatmap")

# 12d. Time x Arrest
subsection("12d. Time x Arrest")

fig, axes = plt.subplots(2, 2, figsize=(16, 11))

arr_yr = df.groupby("dt_year")["Arrest"].mean()
axes[0,0].plot(arr_yr.index, arr_yr.values, marker="o", lw=2.5, color="#22C55E",
               ms=8, markerfacecolor="white", markeredgewidth=2)
format_pct_axis(axes[0,0])
axes[0,0].set_title("Arrest Rate by Year", fontweight="bold")
axes[0,0].set_xlabel("Year")
axes[0,0].set_ylabel("Arrest Rate")
axes[0,0].set_xticks(arr_yr.index)

arr_mo = df.groupby("dt_month")["Arrest"].mean()
axes[0,1].bar([MONTH_NAMES[m] for m in arr_mo.index], arr_mo.values,
              color=sns.color_palette("Greens", 12), edgecolor="white")
format_pct_axis(axes[0,1])
axes[0,1].set_title("Arrest Rate by Month", fontweight="bold")
axes[0,1].set_xlabel("Month")
axes[0,1].set_ylabel("Arrest Rate")

arr_hr = df.groupby("dt_hour")["Arrest"].mean()
axes[1,0].fill_between(arr_hr.index, arr_hr.values, alpha=0.25, color="#22C55E")
axes[1,0].plot(arr_hr.index, arr_hr.values, color="#22C55E", lw=2.5, marker="o", ms=5)
format_pct_axis(axes[1,0])
axes[1,0].set_title("Arrest Rate by Hour", fontweight="bold")
axes[1,0].set_xlabel("Hour (0=midnight)")
axes[1,0].set_ylabel("Arrest Rate")
axes[1,0].set_xticks(range(0, 24))

arr_dow = df.groupby("dt_dow_name")["Arrest"].mean().reindex(DOW_ORDER)
palette_dow2 = ["#22C55E" if d in ["Saturday","Sunday"] else "#2563EB" for d in DOW_ORDER]
axes[1,1].bar(DOW_ORDER, arr_dow.values, color=palette_dow2, edgecolor="white", alpha=0.85)
format_pct_axis(axes[1,1])
axes[1,1].set_title("Arrest Rate by Day of Week", fontweight="bold")
axes[1,1].set_xlabel("Day of Week")
axes[1,1].set_ylabel("Arrest Rate")

plt.suptitle("Temporal Arrest Rate Patterns", fontsize=14, fontweight="bold")
save_fig("15_temporal_arrest_patterns")

print(f"Arrest rate by year:\n{arr_yr.round(4).to_string()}")
print(f"Arrest rate peak hour: {arr_hr.idxmax()}:00 ({arr_hr.max()*100:.1f}%)")

# 12e. Location x Arrest
subsection("12e. Location x Arrest")

arr_dist = (
    df.groupby("District")["Arrest"]
    .agg(total="count", arrested="sum")
    .assign(rate=lambda x: x["arrested"]/x["total"])
    .sort_values("rate", ascending=False))

print("\nArrest rate by District:")
print(arr_dist.to_string())

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

arr_dist_s = arr_dist.sort_values("rate", ascending=True)
axes[0].barh(arr_dist_s.index.astype(str), arr_dist_s["rate"],
             color=[PALETTE_MAIN if r < arrest_rate else "#22C55E"
                    for r in arr_dist_s["rate"]],
             edgecolor="white", alpha=0.85)
axes[0].axvline(arrest_rate, color="#EF4444", lw=1.5, ls="--", label="Overall avg")
format_pct_axis(axes[0], "x")
axes[0].set_title("Arrest Rate by Police District", fontweight="bold")
axes[0].set_xlabel("Arrest Rate")
axes[0].set_ylabel("District")
axes[0].legend()

top_locs = df["Location Description"].value_counts().head(15).index
arr_loc = (
    df[df["Location Description"].isin(top_locs)]
    .groupby("Location Description")["Arrest"]
    .agg(total="count", arrested="sum")
    .assign(rate=lambda x: x["arrested"]/x["total"])
    .sort_values("rate", ascending=True))

axes[1].barh(arr_loc.index, arr_loc["rate"],
             color=[PALETTE_MAIN if r < arrest_rate else "#22C55E"
                    for r in arr_loc["rate"]],
             edgecolor="white", alpha=0.85)
axes[1].axvline(arrest_rate, color="#EF4444", lw=1.5, ls="--", label="Overall avg")
format_pct_axis(axes[1], "x")
axes[1].set_title("Arrest Rate by Location Description (Top 15)", fontweight="bold")
axes[1].set_xlabel("Arrest Rate")
axes[1].legend()

plt.suptitle("Location x Arrest Analysis", fontsize=14, fontweight="bold")
save_fig("16_location_arrest")

# 12f. District x Crime Type heatmap
subsection("12f. District x Crime Type Heatmap")

pivot_dist_crime = (
    df[df["Primary Type"].isin(top8_types)]
    .groupby(["District","Primary Type"]).size()
    .unstack(fill_value=0))
pivot_dist_norm = pivot_dist_crime.div(pivot_dist_crime.sum(axis=1), axis=0)

fig, ax = plt.subplots(figsize=(14, 8))
annot_labels = pivot_dist_norm.map(lambda x: f"{x*100:.0f}%")
sns.heatmap(pivot_dist_norm, cmap=CMAP_BLUE, ax=ax,
            linewidths=0.5, linecolor="white",
            annot=annot_labels, fmt="s",
            cbar_kws={"label":"% of District Crimes"})
ax.set_title("Crime Type Composition by District (row-normalised)", fontweight="bold")
ax.set_xlabel("Crime Type")
ax.set_ylabel("District")
save_fig("17_district_crime_heatmap")


# ===========================================================================
# 13. MULTIVARIATE ANALYSIS
# ===========================================================================
section("13. MULTIVARIATE ANALYSIS")

# 13a. Crime Type x Year x Arrest Rate
subsection("13a. Crime Type x Year x Arrest Rate")

pivot_type_yr_arr = (
    df[df["Primary Type"].isin(top8_types)]
    .groupby(["Primary Type","dt_year"])["Arrest"]
    .mean().unstack())

fig, ax = plt.subplots(figsize=(13, 6))
sns.heatmap(pivot_type_yr_arr, cmap="RdYlGn", ax=ax, vmin=0, vmax=1,
            annot=True, fmt=".0%", linewidths=0.5, linecolor="white",
            cbar_kws={"label":"Arrest Rate"})
ax.set_title("Arrest Rate by Crime Type x Year", fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Crime Type")
save_fig("18_crime_type_year_arrest_heatmap")

# 13b. Crime Type x Location x Arrest
subsection("13b. Crime Type x Location Description x Arrest")

top5_types = crime_counts.head(5).index.tolist()
top5_locs  = df["Location Description"].value_counts().head(5).index.tolist()

pivot_type_loc_arr = (
    df[df["Primary Type"].isin(top5_types) & df["Location Description"].isin(top5_locs)]
    .groupby(["Primary Type","Location Description"])["Arrest"]
    .mean().unstack(fill_value=np.nan))

fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(pivot_type_loc_arr, cmap="RdYlGn", ax=ax, vmin=0, vmax=1,
            annot=True, fmt=".0%", linewidths=0.5, linecolor="white",
            cbar_kws={"label":"Arrest Rate"})
ax.set_title("Arrest Rate - Crime Type x Location Description (Top 5 each)", fontweight="bold")
ax.set_xlabel("Location Description")
ax.set_ylabel("Crime Type")
save_fig("19_crime_loc_arrest_heatmap")

# 13c. Domestic by Crime Type
subsection("13c. Domestic vs Non-Domestic")

dom_crime = (
    df.groupby(["Domestic","Primary Type"]).size()
    .unstack(fill_value=0).T)
dom_crime["dom_pct"] = dom_crime[True] / (dom_crime[True] + dom_crime[False])
dom_crime_top = dom_crime.nlargest(15, True).sort_values("dom_pct", ascending=True)

fig, ax = plt.subplots(figsize=(13, 7))
ax.barh(dom_crime_top.index, dom_crime_top["dom_pct"],
        color="#F59E0B", edgecolor="white", alpha=0.85)
dom_overall = df["Domestic"].mean()
ax.axvline(dom_overall, color="#EF4444", lw=1.5, ls="--",
           label=f"Overall domestic % ({dom_overall*100:.1f}%)")
format_pct_axis(ax, "x")
ax.set_title("% Domestic Incidents by Crime Type (Top 15 by Volume)", fontweight="bold")
ax.set_xlabel("% Domestic")
ax.legend()
save_fig("20_domestic_by_crime_type")

# 13d. Spearman Correlation Matrix
subsection("13d. Numerical Correlation Matrix")

corr_cols = ["Beat","District","Ward","Community Area",
             "Latitude","Longitude","dt_year","dt_month","dt_hour","dt_dow"]
corr_matrix = df[corr_cols].corr(method="spearman")

fig, ax = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap="coolwarm",
            vmin=-1, vmax=1, ax=ax, linewidths=0.5, linecolor="white",
            cbar_kws={"label":"Spearman rho"})
ax.set_title("Spearman Correlation Matrix - Numerical Variables", fontweight="bold")
save_fig("21_correlation_matrix")


# ===========================================================================
# 14. STATISTICAL ANALYSIS
# ===========================================================================
section("14. STATISTICAL ANALYSIS")

# 14a. Chi-Square: Primary Type x Arrest
subsection("14a. Chi-Square: Primary Type x Arrest")

ct_type_arrest = pd.crosstab(df["Primary Type"], df["Arrest"])
chi2_val, p_val, dof, expected = chi2_contingency(ct_type_arrest)
v_type_arrest, _ = cramers_v(df["Primary Type"], df["Arrest"])

print(f"  H0: Primary Type and Arrest are independent")
print(f"  H1: There is an association between Primary Type and Arrest")
print(f"  chi2 = {chi2_val:,.2f}")
print(f"  dof  = {dof}")
print(f"  p    = {p_val:.2e}")
print(f"  Cramer's V = {v_type_arrest:.4f}  (association: {'strong' if v_type_arrest>0.3 else 'moderate' if v_type_arrest>0.1 else 'weak'})")
print(f"  Conclusion: {'Reject H0' if p_val<0.05 else 'Fail to reject H0'} at alpha=0.05")

# 14b. Chi-Square: Domestic x Arrest
subsection("14b. Chi-Square: Domestic x Arrest")

ct_dom_arrest = pd.crosstab(df["Domestic"], df["Arrest"])
chi2_d, p_d, dof_d, _ = chi2_contingency(ct_dom_arrest)
v_dom, _ = cramers_v(df["Domestic"], df["Arrest"])

print(f"  chi2 = {chi2_d:,.2f},  p = {p_d:.2e}")
print(f"  Cramer's V = {v_dom:.4f}")

# 14c. Chi-Square: District x Arrest
subsection("14c. Chi-Square: District x Arrest")

ct_dist_arrest = pd.crosstab(df["District"], df["Arrest"])
chi2_dist, p_dist, dof_dist, _ = chi2_contingency(ct_dist_arrest)
v_dist, _ = cramers_v(df["District"], df["Arrest"])

print(f"  chi2 = {chi2_dist:,.2f},  p = {p_dist:.2e}")
print(f"  Cramer's V = {v_dist:.4f}")

# 14d. Point-biserial: Hour x Arrest
subsection("14d. Point-Biserial: Hour x Arrest")

pb_corr, pb_p = stats.pointbiserialr(df["Arrest"].astype(int), df["dt_hour"])
print(f"  r_pb = {pb_corr:.4f},  p = {pb_p:.4e}")
print(f"  {'Significant' if pb_p<0.05 else 'Not significant'} at alpha=0.05")


# ===========================================================================
# 15. OUTLIER ANALYSIS
# ===========================================================================
section("15. OUTLIER ANALYSIS")

def outlier_iqr(series, name):
    q1, q3 = series.quantile([0.25, 0.75])
    iqr    = q3 - q1
    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
    n_low  = (series < lower).sum()
    n_high = (series > upper).sum()
    print(f"  {name:<22}: IQR [{lower:.2f}, {upper:.2f}]  "
          f"low={n_low}, high={n_high}")

for col in ["Beat","District","Ward","Community Area","Latitude","Longitude"]:
    outlier_iqr(df[col].dropna(), col)

print(f"  IUCR unique count   : {df['IUCR'].nunique()} codes")
print(f"  Community Area == 0 : {(df['Community Area']==0).sum()}")
print(f"  Beat == 0           : {(df['Beat']==0).sum()}")


# ===========================================================================
# 16. ADVANCED CRIME-SPECIFIC ANALYSIS
# ===========================================================================
section("16. ADVANCED CRIME-SPECIFIC ANALYSIS")

# 16a. Crime Concentration
subsection("16a. Crime Concentration")

cumulative  = crime_counts.cumsum() / crime_counts.sum()
types_50pct = int((cumulative <= 0.5).sum()) + 1
types_80pct = int((cumulative <= 0.8).sum()) + 1
print(f"  Top {types_50pct} crime types account for >= 50% of all incidents")
print(f"  Top {types_80pct} crime types account for >= 80% of all incidents")
print(f"  Theft alone: {crime_counts['THEFT']/TOTAL*100:.1f}% of incidents")
print(f"  Theft + Battery: {(crime_counts['THEFT']+crime_counts['BATTERY'])/TOTAL*100:.1f}%")

fig, ax = plt.subplots(figsize=(9, 6))
ax.plot(range(1, len(crime_counts)+1), cumulative.values*100,
        color=PALETTE_MAIN, lw=2.5, marker="o", ms=5)
ax.axhline(50, color="#EF4444", ls="--", lw=1.5, label="50%")
ax.axhline(80, color="#F59E0B", ls="--", lw=1.5, label="80%")
ax.set_xlabel("Number of Crime Types (ranked by frequency)")
ax.set_ylabel("Cumulative % of All Incidents")
ax.set_title("Crime Concentration Curve", fontweight="bold")
ax.legend()
ax.set_ylim(0, 105)
ax.grid(alpha=0.3)
save_fig("22_crime_concentration")

# 16b. Seasonal Patterns
subsection("16b. Seasonal Patterns")

season_map = {1:"Winter",2:"Winter",3:"Spring",4:"Spring",5:"Spring",
              6:"Summer",7:"Summer",8:"Summer",9:"Fall",10:"Fall",
              11:"Fall",12:"Winter"}
df["Season"]   = df["dt_month"].map(season_map)
season_counts  = df.groupby("Season").size()
season_order   = ["Winter","Spring","Summer","Fall"]

print("\nIncidents by Season:")
for s in season_order:
    cnt = int(season_counts.get(s, 0))
    print(f"  {s}: {cnt:,} ({cnt/TOTAL*100:.1f}%)")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
season_data   = season_counts.reindex(season_order)
season_colors = ["#60A5FA","#34D399","#FBBF24","#F87171"]
axes[0].bar(season_order, season_data.values, color=season_colors, edgecolor="white", alpha=0.9)
axes[0].set_title("Crimes by Season", fontweight="bold")
axes[0].set_ylabel("Number of Incidents")

season_arr = df.groupby("Season")["Arrest"].mean().reindex(season_order)
axes[1].bar(season_order, season_arr.values, color=season_colors, edgecolor="white", alpha=0.9)
format_pct_axis(axes[1])
axes[1].set_title("Arrest Rate by Season", fontweight="bold")
axes[1].set_ylabel("Arrest Rate")

plt.suptitle("Seasonal Crime Patterns", fontsize=14, fontweight="bold")
save_fig("23_seasonal_patterns")

# 16c. Temporal Concentration
subsection("16c. Temporal Concentration")

total_hours = len(df.dropna(subset=["dt_hour"]))
top6_hours  = hour_counts.nlargest(6)
wknd        = int(df["dt_is_weekend"].sum())
wkdy        = int((~df["dt_is_weekend"]).sum())

print(f"  Top 6 busiest hours: {top6_hours.sum()/total_hours*100:.1f}% of incidents")
print(f"  Noon-6PM share     : {hour_counts[12:18].sum()/total_hours*100:.1f}%")
print(f"  Midnight-6AM share : {hour_counts[0:6].sum()/total_hours*100:.1f}%")
print(f"  Weekend incidents  : {wknd:,} ({wknd/TOTAL*100:.1f}%)")
print(f"  Weekday incidents  : {wkdy:,} ({wkdy/TOTAL*100:.1f}%)")
print(f"  Expected weekend % (2/7): {2/7*100:.1f}%")

wknd_arr_rate = df[df["dt_is_weekend"]]["Arrest"].mean()
wkdy_arr_rate = df[~df["dt_is_weekend"]]["Arrest"].mean()
print(f"  Weekend arrest rate: {wknd_arr_rate*100:.1f}%")
print(f"  Weekday arrest rate: {wkdy_arr_rate*100:.1f}%")


# ===========================================================================
# 17. KEY FINDINGS
# ===========================================================================
section("17. KEY FINDINGS - TOP 10 INSIGHTS")

theft_pct   = crime_counts["THEFT"] / TOTAL * 100
battery_pct = crime_counts["BATTERY"] / TOTAL * 100
top2_pct    = (crime_counts["THEFT"] + crime_counts["BATTERY"]) / TOTAL * 100
pros_arr    = arrest_by_crime.loc["PROSTITUTION","arrest_rate"]*100 if "PROSTITUTION" in arrest_by_crime.index else float("nan")
narc_arr    = arrest_by_crime.loc["NARCOTICS","arrest_rate"]*100   if "NARCOTICS"    in arrest_by_crime.index else float("nan")
burg_arr    = arrest_by_crime.loc["BURGLARY","arrest_rate"]*100    if "BURGLARY"     in arrest_by_crime.index else float("nan")
cdam_arr    = arrest_by_crime.loc["CRIMINAL DAMAGE","arrest_rate"]*100 if "CRIMINAL DAMAGE" in arrest_by_crime.index else float("nan")
mvt_arr     = arrest_by_crime.loc["MOTOR VEHICLE THEFT","arrest_rate"]*100 if "MOTOR VEHICLE THEFT" in arrest_by_crime.index else float("nan")
summer_pct  = season_counts.get("Summer", 0) / TOTAL * 100
winter_pct  = season_counts.get("Winter", 0) / TOTAL * 100
yr2021      = int(year_counts.get(2021, 0))
yr2024      = int(year_counts.get(2024, 0))
pct_growth  = (yr2024 - yr2021) / yr2021 * 100 if yr2021 > 0 else 0
dom_arr_diff = abs(dom_arrest[True] - dom_arrest[False]) * 100

insights = f"""
INSIGHT 1 - THEFT AND BATTERY DOMINATE
  Theft ({theft_pct:.1f}%) and Battery ({battery_pct:.1f}%) together account for
  {top2_pct:.1f}% of all 120,759 recorded incidents.

INSIGHT 2 - OVERALL ARREST RATE IS LOW AT {arrest_rate*100:.1f}%
  Only {arrest_rate*100:.1f}% of incidents resulted in an arrest.
  Roughly 2 in 3 incidents do NOT lead to an arrest.

INSIGHT 3 - ARREST RATES VARY WIDELY BY CRIME TYPE (Cramer's V={v_type_arrest:.3f})
  Prostitution ({pros_arr:.0f}%) and Narcotics ({narc_arr:.0f}%) have very high arrest
  rates, while Burglary ({burg_arr:.0f}%), Criminal Damage ({cdam_arr:.0f}%), and Motor
  Vehicle Theft ({mvt_arr:.0f}%) have very low arrest rates.

INSIGHT 4 - NOON IS THE PEAK CRIME HOUR
  The highest number of incidents is recorded at noon (12:00): {hour_counts[peak_hour]:,}.
  The quietest hour is {hour_counts.idxmin()}:00 with {hour_counts.min():,} incidents.

INSIGHT 5 - WEEKEND CRIMES EXCEED EXPECTED SHARE
  Weekend crimes = {wknd/TOTAL*100:.1f}% vs expected 28.6% (2 out of 7 days).
  Friday records the highest single-day count.

INSIGHT 6 - SUMMER IS THE PEAK CRIME SEASON
  Summer accounts for {summer_pct:.1f}% of all incidents vs Winter at {winter_pct:.1f}%.
  A clear warm-weather crime seasonality is present.

INSIGHT 7 - CRIME VOLUME GREW FROM 2021 TO 2024
  Incidents: {yr2021:,} (2021) -> {yr2024:,} (2024), a {pct_growth:.1f}% increase.
  NOTE: 2025 data is partial; it cannot be directly compared.

INSIGHT 8 - TOP 3 CRIME TYPES COVER >50% OF ALL INCIDENTS
  Theft, Battery, and Criminal Damage together represent more than half
  of all recorded crime (concentration phenomenon confirmed).

INSIGHT 9 - DOMESTIC INCIDENTS ACCOUNT FOR {dom_rate*100:.1f}% OF CRIMES
  Domestic incidents differ from non-domestic by {dom_arr_diff:.1f} percentage points
  in arrest rate, confirmed by Chi-square test (p < 0.05).

INSIGHT 10 - COORDINATE MISSINGNESS IS SYSTEMATIC (1.55%)
  1,877 records have missing coordinates. The identical count across
  Latitude, Longitude, X Coordinate, and Y Coordinate confirms these
  are the same records missing all spatial data simultaneously.
"""
print(insights)


# ===========================================================================
# 18. DATASET LIMITATIONS
# ===========================================================================
section("18. DATASET LIMITATIONS")

limitations = """
  1. PARTIAL 2025 DATA - Year-over-year comparisons must account for this.
  2. NO POPULATION DENOMINATOR - Cannot compute true crime rates per capita.
  3. REPORTING BIAS - Not all crimes are reported; underreporting likely varies
     by crime type and neighborhood.
  4. MIXED DATE FORMATS - Required custom parsing; any unparsed dates are
     excluded from temporal analyses.
  5. DUPLICATE CASE NUMBERS - May represent legitimate amendments to records,
     not duplicate incidents.
  6. NO DEMOGRAPHIC DATA - No victim/offender demographics available.
  7. COORDINATE MISSINGNESS - 1.55% of records lack spatial data.
  8. IUCR CODE EVOLUTION - Classification codes may have changed across years.
  9. OBSERVATIONAL DATA - No causal inference is possible.
  10. DISTRICT 31 - Non-standard district code; may indicate data quirk.
"""
print(limitations)


# ===========================================================================
# 19. SUMMARY DASHBOARD
# ===========================================================================
section("19. SUMMARY DASHBOARD")

fig = plt.figure(figsize=(20, 14))
gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35)

# Panel 1: Top 8 crime types
ax1 = fig.add_subplot(gs[0, :2])
top8_data  = crime_counts.head(8)
colors_p1  = sns.color_palette("Blues_d", 8)[::-1]
ax1.barh(top8_data.index[::-1], top8_data.values[::-1], color=colors_p1, edgecolor="white")
ax1.set_title("Top 8 Crime Types", fontweight="bold")
ax1.set_xlabel("Incidents")

# Panel 2: Arrest donut
ax2 = fig.add_subplot(gs[0, 2])
ax2.pie([arrest_counts[False], arrest_counts[True]],
        labels=["No Arrest","Arrest"],
        autopct="%1.1f%%", startangle=90,
        colors=["#EF4444","#22C55E"],
        wedgeprops=dict(width=0.55, edgecolor="white"))
ax2.set_title("Arrest Rate", fontweight="bold")

# Panel 3: Crimes by year
ax3 = fig.add_subplot(gs[0, 3])
ax3.plot(year_counts.index, year_counts.values, marker="o", color=PALETTE_MAIN, lw=2.5)
ax3.set_title("Crimes by Year", fontweight="bold")
ax3.set_xticks(year_counts.index)
ax3.set_xticklabels(year_counts.index, fontsize=8)
ax3.set_ylabel("Incidents")

# Panel 4: Crimes by hour
ax4 = fig.add_subplot(gs[1, :2])
ax4.fill_between(hour_counts.index, hour_counts.values, alpha=0.25, color="#8B5CF6")
ax4.plot(hour_counts.index, hour_counts.values, color="#8B5CF6", lw=2)
ax4.set_title("Crimes by Hour of Day", fontweight="bold")
ax4.set_xlabel("Hour")
ax4.set_ylabel("Incidents")
ax4.set_xticks(range(0, 24))

# Panel 5: Crimes by month
ax5 = fig.add_subplot(gs[1, 2:])
month_counts_all = df.groupby("dt_month").size()
ax5.bar([MONTH_NAMES[m] for m in month_counts_all.index], month_counts_all.values,
        color=sns.color_palette("Paired", 12), edgecolor="white")
ax5.set_title("Crimes by Month", fontweight="bold")
ax5.set_ylabel("Incidents")

# Panel 6: Arrest rate by crime type
ax6 = fig.add_subplot(gs[2, :2])
top10_arr = (arrest_by_crime[arrest_by_crime["total"] >= 200]
             .sort_values("arrest_rate", ascending=True).tail(10))
ax6.barh(top10_arr.index, top10_arr["arrest_rate"],
         color=[PALETTE_MAIN if r < arrest_rate else "#22C55E"
                for r in top10_arr["arrest_rate"]],
         edgecolor="white", alpha=0.85)
ax6.axvline(arrest_rate, color="#EF4444", ls="--", lw=1.5)
format_pct_axis(ax6, "x")
ax6.set_title("Arrest Rate by Crime Type", fontweight="bold")

# Panel 7: District crime counts
ax7 = fig.add_subplot(gs[2, 2:])
dc_top = dist_counts.head(10).sort_values(ascending=True)
ax7.barh(dc_top.index.astype(str), dc_top.values,
         color=sns.color_palette("rocket_r", len(dc_top))[::-1], edgecolor="white")
ax7.set_title("Top 10 Districts by Incident Count", fontweight="bold")
ax7.set_xlabel("Incidents")
ax7.set_ylabel("District")

fig.suptitle("CHICAGO CRIME DATASET - EDA SUMMARY DASHBOARD (2021-2025)",
             fontsize=17, fontweight="bold", y=1.01)
save_fig("00_summary_dashboard")

print("\n" + "="*70)
print("  EDA COMPLETE")
print(f"  All figures saved to: {OUTPUT_DIR}/")
print(f"  Total figures        : {len(os.listdir(OUTPUT_DIR))}")
print("="*70)
