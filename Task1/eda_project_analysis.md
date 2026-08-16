# Comprehensive Analysis of Chicago Crime EDA Project

Here is a thorough, step-by-step breakdown of your Exploratory Data Analysis project based entirely on the `chicago_crime_eda.py` script you provided.

---

## 1. Project Overview

*   **Objective:** The objective of this project is to perform a comprehensive Exploratory Data Analysis (EDA) on Chicago crime data to uncover spatial, temporal, and categorical patterns, and to understand the factors associated with arrests.
*   **Dataset Representation:** The dataset (`chicago_crime_dataset.csv`) represents reported incidents of crime that occurred in the city of Chicago.
*   **Target/Question:** While EDA doesn't explicitly have a "target variable" like supervised machine learning, the project heavily investigates the `Arrest` column (whether an arrest was made) and how it relates to time, location, and crime type.
*   **Important Columns:**
    *   `ID` / `Case Number`: Unique identifiers for the incident.
    *   `Date`: When the incident occurred.
    *   `Primary Type`: The main classification of the crime (e.g., THEFT, BATTERY).
    *   `Description`: More detailed breakdown of the crime.
    *   `Location Description`: Where it happened (e.g., STREET, APARTMENT).
    *   `Arrest`: Boolean flag (True/False) indicating if an arrest was made.
    *   `Domestic`: Boolean flag indicating if the incident was domestic-related.
    *   `Beat`, `District`, `Ward`, `Community Area`: Geographic and police jurisdictions.
    *   `Latitude`, `Longitude`: Exact spatial coordinates.
*   **Data Types of Important Columns:** Mixed. Identifiers are integers/strings, dates start as strings, categories are strings, coordinates are floats, and `Arrest`/`Domestic` are booleans.
*   **Dataset Size:** 120,759 rows and 22 initial columns (which shrinks to 21 after dropping `_year`).

---

## 2. Data Loading

*   **How the dataset was loaded:** The dataset is loaded using the `pandas` library.
*   **Code:** `df_raw = pd.read_csv(DATASET_PATH)`
*   **Why this method:** `pd.read_csv()` is the standard, highly optimized Pandas function for reading comma-separated values files into a DataFrame (a 2D tabular data structure). It automatically infers basic data types.

---

## 3. Initial Data Understanding

Here is how you inspected the data right after loading:

*   **`df_raw.shape`**: Returns a tuple (rows, columns). *Why:* To know the exact size of the dataset (120,759 x 22).
*   **`df_raw.memory_usage(deep=True).sum()`**: Calculates RAM usage. *Why:* To ensure the dataset fits comfortably in memory.
*   **`df_raw.columns.tolist()`**: Prints the names of all columns. *Why:* To verify the schema matches expectations.
*   **`df_raw.head(5)` & `df_raw.tail(5)`**: Prints the first and last 5 rows. *Why:* To get a visual sense of what the data looks like, spot obvious formatting issues, and ensure the start/end of the file loaded correctly.
*   **`df_raw.sample(5, random_state=42)`**: Prints 5 random rows. *Why:* `head` and `tail` can be biased (e.g., if data is sorted by date). Sampling gives a more representative look at the data.
*   **`df_raw.dtypes`**: Prints the data type of each column. *Why:* To see if pandas guessed the types correctly (e.g., realizing `Date` is currently a string/object, not a datetime).

---

## 4. Data Cleaning

Here are the specific cleaning steps performed in your code:

**1. Redundant Column Removal**
*   **Problem:** The dataset had a column `_year` and `Year`. 
*   **Detection:** By inspecting columns, you suspected they were duplicates. You verified it with `assert (df_raw['_year'] == df_raw['Year']).all()`.
*   **Fix:** `df_raw = df_raw.drop(columns=["_year"])`
*   **Why:** To reduce dimensionality and memory usage. Keeping duplicate data is confusing and inefficient.

**2. Handling Mixed Date Formats**
*   **Problem:** The `Date` column contained strings in two different formats (`MM/DD/YYYY HH:MM:SS AM/PM` and `MM-DD-YYYY HH:MM`). Standard `pd.to_datetime` would fail on one or the other.
*   **Detection:** This was likely discovered when a standard parsing attempt failed.
*   **Fix:** You wrote a custom function `parse_mixed_dates` that first tries Format A, and for any rows that result in NaT (Not a Time), it targets them specifically using a boolean mask (`parsed.isna()`) and parses them with Format B.
*   **Why:** Without a unified datetime column, no time-series analysis (crimes by hour, month) is possible.

**3. Handling Invalid Coordinates**
*   **Problem:** Some rows had exactly `0` for `X Coordinate` and `Y Coordinate`.
*   **Detection:** You counted them: `(df["X Coordinate"] == 0).sum()`.
*   **Fix:** `df.loc[df["X Coordinate"]==0, ["X Coordinate","Y Coordinate","Latitude","Longitude","Location"]] = np.nan`
*   **Why:** 0,0 is off the coast of Africa. It represents a missing value (or data entry error) in Chicago state-plane coordinates, not an actual location. Setting them to NaN prevents them from messing up spatial plots.

**4. Flagging Duplicates**
*   **Problem:** There were identical `Case Number`s across multiple rows.
*   **Detection:** `df[df.duplicated("Case Number", keep=False)]`.
*   **Fix:** You intentionally *did not* drop them. You logged them.
*   **Why:** In police data, duplicate case numbers often represent updates to a case or multiple charges stemming from the same incident, not necessarily dirty data.

*(Note: Missing values were quantified via `.isna().sum()` and visualized, but outside of coordinates, they were largely retained because dropping them would lose valuable information in other columns).*

---

## 5. Univariate Analysis

Univariate analysis looks at one variable at a time to understand its distribution.

**1. Numerical Variable Distributions (Beat, District, Ward, Latitude, etc.)**
*   **Analysis:** Plotted Histograms (with KDE lines) and Boxplots.
*   **Why:** Histograms show the shape of the data (Distribution, Skewness). Boxplots highlight the Median, IQR, and Outliers.
*   **Observation:** Shows which police districts/beats handle the most volume, and shows the geographic spread of latitudes/longitudes.

**2. Crime Type (Categorical)**
*   **Analysis:** Bar chart of top 15 `Primary Type`s and a Pie chart of the top 8.
*   **Why:** To see which crimes are most prevalent (Frequency/Count).
*   **Observation:** THEFT and BATTERY dominate the dataset.

**3. Arrest Rate (Categorical/Boolean)**
*   **Analysis:** Donut chart of overall Arrest (True) vs No Arrest (False).
*   **Why:** To establish a baseline metric.
*   **Observation:** The overall arrest rate is low (majority of crimes do not end in arrest).

**4. Temporal Patterns (Dates/Times)**
*   **Analysis:** Line chart for Years, Bar charts for Months and Days of Week, Line/Area chart for Hours.
*   **Why:** To find seasonal and daily rhythms in crime.
*   **Observation:** Crime peaks at Noon, drops at night. Summer months have more crime than winter. Weekends have higher volume than expected.

**5. Geographic Patterns (Location/District)**
*   **Analysis:** Bar charts of incidents per District and Location Description, plus a scatter plot of Lat/Lon.
*   **Why:** To see where crimes happen most often.
*   **Observation:** Streets and Apartments are top locations.

**Statistical Concepts Connected to Your Data:**
*   **Distribution:** How crime counts are spread across hours of the day.
*   **Mean/Median:** Calculated for numerical columns (like District). If Mean > Median, it indicates right-skewness.
*   **Skewness:** You explicitly calculated this for numerical columns. A high skew means the data leans heavily to one side.
*   **Frequency/Count:** Used constantly via `.value_counts()` to rank Crime Types and Locations.

---

## 6. Bivariate Analysis

Bivariate analysis looks at the relationship between exactly two variables.

**1. Crime Type vs Arrest (Categorical vs Categorical)**
*   **Variables:** `Primary Type` and `Arrest`.
*   **Graph:** Side-by-side horizontal bar chart showing Arrest Rate per crime type.
*   **Observation:** Prostitution and Narcotics have extremely high arrest rates; Burglary and Motor Vehicle Theft have extremely low ones.
*   **Conclusion:** The type of crime heavily dictates the likelihood of an arrest.

**2. Crime Type vs Year (Categorical vs Temporal)**
*   **Variables:** Top 8 `Primary Type`s and `Year`.
*   **Graph:** Line chart with multiple lines (one for each crime type).
*   **Observation:** Shows if specific crimes are trending up or down over the 2021-2025 period.

**3. Time vs Arrest (Temporal vs Categorical)**
*   **Variables:** Hour/Month/Day and `Arrest`.
*   **Graph:** Line/Bar charts showing arrest rate fluctuating over time.
*   **Observation:** You can see what time of day police are most likely to make an arrest.

**4. Location vs Arrest (Categorical vs Categorical)**
*   **Variables:** `District` / `Location Description` and `Arrest`.
*   **Graph:** Bar charts colored conditionally (green if above average arrest rate, blue if below).
*   **Observation:** Arrest rates fluctuate wildly depending on which district the crime occurs in, or if it happens on a street vs an apartment.

---

## 7. Multivariate Analysis

Multivariate analysis looks at three or more variables simultaneously.

**1. Arrest Rate by Crime Type and Year**
*   **Variables:** `Primary Type`, `Year`, `Arrest`.
*   **Graph:** Heatmap (`sns.heatmap`).
*   **Observation:** Allows you to see if the arrest rate for a *specific* crime type is improving or worsening over time.

**2. Arrest Rate by Crime Type and Location**
*   **Variables:** `Primary Type`, `Location Description`, `Arrest`.
*   **Graph:** Heatmap.
*   **Observation:** Shows interactions. For example, is a theft on the street more likely to result in an arrest than a theft in a residence?

**3. Correlation Matrix**
*   **Variables:** All numerical features (Beat, District, Ward, Lat, Lon, Hour, Year, etc.).
*   **Graph:** Heatmap of Spearman Correlation.
*   **Explanation of Correlation:**
    *   **Correlation** measures how two variables move together.
    *   **+1:** Perfect positive correlation (as X goes up, Y goes up).
    *   **-1:** Perfect negative correlation (as X goes up, Y goes down).
    *   **0:** No linear relationship.
    *   **Correlation vs Causation:** Just because two things move together doesn't mean one causes the other. For example, if Ward and District correlate highly, it's just because they are overlapping geographic designations, not because one causes the other.
*   **Your Data:** You used Spearman correlation because variables like 'District' are ordinal/categorical numbers, not continuous scales, and Spearman handles non-linear relationships better.

---

## 8. Feature Engineering

Feature engineering is creating new data from existing data to expose patterns to models or analysts.

**1. Temporal Features**
*   **Original Data:** `Date_parsed` (e.g., "2021-11-24 12:00:00")
*   **New Features:** `dt_year`, `dt_month`, `dt_day`, `dt_hour`, `dt_dow`, `dt_dow_name`, `dt_quarter`
*   **Code:** `df["dt_year"] = df["Date_parsed"].dt.year`
*   **Why:** ML models and groupby functions cannot easily read raw timestamps. Breaking them apart allows you to ask "what happens on Tuesdays?" or "what happens at 2 AM?".

**2. Boolean Time Flags**
*   **Original Data:** `dt_dow` and `dt_hour`
*   **New Features:** `dt_is_weekend` and `dt_night`
*   **Code:** `df["dt_is_weekend"] = df["dt_dow"].isin([5, 6])`
*   **Why:** Groups granular data into meaningful business concepts. "Night" behaves differently than "Day".

**3. Seasonality**
*   **Original Data:** `dt_month`
*   **New Feature:** `Season` (Winter, Spring, Summer, Fall)
*   **Code:** Used a dictionary mapping (`season_map`) and `.map()`.
*   **Why:** To perform seasonal analysis and prove that Summer has more crime than Winter.

---

## 9. Outlier Analysis

*   **What is an outlier?** A data point that differs significantly from other observations. It could be an error or a rare, legitimate event.
*   **How detected:** You used the **IQR (Interquartile Range) method**.
*   **IQR Explained:** 
    *   Find the 25th percentile (Q1) and 75th (Q3).
    *   Calculate IQR = Q3 - Q1.
    *   Any value below (Q1 - 1.5 * IQR) or above (Q3 + 1.5 * IQR) is flagged as an outlier.
*   **In your project:** You ran `outlier_iqr()` on Beat, District, Ward, Latitude, and Longitude. 
*   **Decision:** You *retained* them (except for 0,0 coordinates). 
*   **Why:** In geographic data, an "outlier" latitude just means a crime happened on the edge of the city limits. It's a valid data point, not an error to be removed.

---

## 10. Important Visualizations

*(Note: These correspond to the figures saved in your `eda_output` folder)*

1.  **Missing Value Analysis (`01_missing_values`)**: Horizontal bar chart & heatmap. *Purpose:* Show data sparsity. *Insight:* Location Description and Coordinates have small (~1.5%) missingness.
2.  **Numerical Distributions (`02_numerical_distributions`)**: Grid of Histograms + Boxplots. *Purpose:* Show the spread of numerical data.
3.  **Top 15 Crime Types (`03_top15_crime_types`)**: Horizontal bar chart. *Insight:* Theft and Battery dominate.
4.  **Crime Type Pie (`04_crime_type_pie`)**: *Insight:* Visualizes the concentration (the top 8 crimes make up the vast majority).
5.  **Arrest Analysis (`06_arrest_analysis`)**: Donut chart + Bar chart. *Insight:* Shows the massive discrepancy in arrest rates across different crime types.
6.  **Temporal Patterns (`07_temporal_patterns`)**: Grid of line/bar charts (Year, Month, Day, Hour). *Purpose:* Expose cycles. *Insight:* Peak hour is noon, peak season is summer.
7.  **Heatmaps (`08_monthly_year`, `09_hour_dow`)**: *Purpose:* Show intensity in 2D space. *Insight:* Fridays at noon might be hotter than Sundays at 3 AM.
8.  **Geographic Scatter (`11_geographic_scatter`)**: Plot of Lat vs Lon. *Purpose:* Literally draws a map of Chicago using crime density.
9.  **Crime Arrest Bivariate (`12_crime_arrest_bivariate`)**: Stacked bar chart showing absolute numbers of Arrested vs Not Arrested per crime.
10. **Summary Dashboard (`00_summary_dashboard`)**: A complex grid layout (using GridSpec) combining the most critical charts into one executive summary.

---

## 11. Statistical Concepts Used

*   **Mean/Average:** The sum of values divided by count. Used in your project to calculate Arrest Rates (because average of [0, 1, 0, 0] is 0.25, or 25%).
*   **Median:** The middle value when sorted. Less sensitive to outliers than the mean.
*   **Standard Deviation / Variance:** Measures how spread out the numbers are.
*   **Quartiles / IQR:** Splitting data into four equal groups. The distance between the 1st and 3rd quartile is the IQR, used to find outliers.
*   **Chi-Square Test of Independence:** A statistical test to see if two categorical variables are related. You used this to prove that `Primary Type` and `Arrest` are statistically dependent (p < 0.05).
*   **Cramer's V:** A number between 0 and 1 indicating how strongly two categorical variables are associated.
*   **Point-Biserial Correlation:** A specific correlation test used when comparing a continuous variable (`dt_hour`) with a binary categorical variable (`Arrest`).

---

## 12. Libraries Used

*   **`pandas`**: The backbone. Used for dataframes, reading CSVs, grouping, aggregating, and reshaping data.
*   **`numpy`**: Used for mathematical operations, creating boolean masks, and handling `np.nan` (missing values).
*   **`matplotlib.pyplot`**: The core charting library used to draw lines, bars, and subplots.
*   **`seaborn`**: A high-level visualization library built on matplotlib. Used specifically for the elegant correlation and 2D heatmaps, and generating color palettes.
*   **`scipy.stats`**: The statistics engine. Used to run the Chi-square and Point-Biserial tests to calculate p-values.

---

## 13. Code Explanation (Key Snippets)

**Parsing Dates:**
```python
parsed = pd.to_datetime(series, format="%m/%d/%Y %I:%M:%S %p", errors="coerce")
mask   = parsed.isna()
parsed[mask] = pd.to_datetime(series[mask], format="%m-%d-%Y %H:%M", errors="coerce")
```
*Explanation:* `pd.to_datetime` tries to convert strings to dates using the first format. `errors="coerce"` means "if it fails, put a NaT (missing value) instead of crashing". The `mask` finds all the rows that failed. We then target only those failed rows (`series[mask]`) and try parsing them again with the second format.

**Creating Heatmap Data:**
```python
pivot_hour_dow = (df.groupby(["dt_dow_name","dt_hour"]).size()
                  .unstack(fill_value=0).reindex(DOW_ORDER))
```
*Explanation:* Groups data by Day of Week AND Hour, then counts the `.size()` of each bucket. This results in a long list. `.unstack()` pivots the Hour index to become columns, turning the list into a 2D matrix. `.reindex()` ensures the days are in Monday-Sunday order, not alphabetical.

**Chi-Square Test:**
```python
ct_type_arrest = pd.crosstab(df["Primary Type"], df["Arrest"])
chi2_val, p_val, dof, expected = chi2_contingency(ct_type_arrest)
```
*Explanation:* `pd.crosstab` creates a frequency table (Rows = Crimes, Columns = Arrest True/False). `chi2_contingency` runs the math on this table and returns the test statistic and the `p_val`. If `p_val` is < 0.05, we reject the null hypothesis and conclude Crime Type affects Arrest probability.

---

## 14. Insights and Conclusions

Based on your script's output, here are the key insights:

**Category & Distribution Insights:**
*   Theft and Battery are the dominant crimes, making up over a massive portion of all incidents.
*   Crime concentration is high: The top 3 crime types cover more than 50% of the dataset.

**Temporal Insights:**
*   Crime peaks at noon (12:00 PM).
*   Weekends observe a disproportionately higher share of crime compared to weekdays.
*   There is clear seasonality: Summer has significantly more crime than Winter.

**Relationship / Arrest Insights:**
*   The overall arrest rate is low.
*   Arrest rates are highly dependent on the crime type. Prostitution and Narcotics almost always result in an arrest; Burglary and Motor Vehicle Theft almost never do.
*   Domestic incidents have a statistically different arrest rate than non-domestic incidents.
*   Arrest rates vary drastically by Police District.

**Data Quality Insights:**
*   Roughly 1.55% of the data systematically lacks spatial coordinates (Lat/Lon/X/Y all missing together).
*   Data entry zeroed out some coordinates (0,0) which had to be cleaned.

---

## 15. What We Can Do Next (ML Preparation)

If you were to build a Machine Learning model (e.g., to predict if an incident will result in an Arrest):

*   **Target Variable:** `Arrest` (Binary Classification).
*   **Useful Features:** `Primary Type`, `dt_hour`, `dt_dow_name`, `Location Description`, `District`, `Domestic`.
*   **Preprocessing Required:**
    *   **Categorical Encoding:** `Primary Type`, `Location Description`, and `dt_dow_name` are text. They must be One-Hot Encoded or Target Encoded into numbers.
    *   **Imputation:** Rows with missing Lat/Lon might need to be dropped, or imputed with the median of their respective District.
    *   **Feature Scaling:** Standardizing coordinates or times if using distance-based models (like KNN).
*   **Potential Problems:**
    *   **Class Imbalance:** Because the overall arrest rate is low, the model might just predict "No Arrest" every time and achieve high accuracy but zero recall. You would need to use SMOTE, class weights, or evaluate using the F1-Score/PR-AUC.
    *   **Data Leakage:** You cannot use features that are only known *after* an arrest happens to predict an arrest.

---

## 16. Viva Preparation (30 Questions)

1.  **What was the primary objective of your EDA?** To uncover spatial, temporal, and categorical patterns in Chicago crime data and understand factors influencing arrest rates.
2.  **How large was your dataset?** 120,759 rows and 22 columns.
3.  **Why did you drop the `_year` column?** It was an exact duplicate of the `Year` column, wasting memory and adding clutter.
4.  **How did you handle dates?** I wrote a custom parser because the data had two mixed string formats. I converted them to datetime objects to extract temporal features.
5.  **What is feature engineering?** Creating new columns from existing data. I extracted Hour, Day of Week, and Season from the Date column.
6.  **Why did you create a `dt_is_weekend` flag?** Because human behavior changes on weekends, meaning crime patterns likely change too. It simplifies the data for modeling.
7.  **What did you do with coordinates that were exactly 0,0?** I replaced them with NaN. 0,0 in this projection is invalid (off the coast of Africa) and represents a data entry error.
8.  **Did you remove missing values?** I retained them. Outside of coordinates, missingness was low, and dropping rows would lose valuable information in other columns.
9.  **What is the difference between Univariate and Bivariate analysis?** Univariate looks at one variable (e.g., a histogram of hours). Bivariate looks at the relationship between two (e.g., Arrest rate by Hour).
10. **Why use a Boxplot?** It visually shows the median, quartiles, and outliers of a numerical distribution.
11. **What were the most common crimes?** Theft and Battery.
12. **How did Arrest rates vary?** Drastically. Narcotics had very high rates, Burglary had very low rates.
13. **What is a Heatmap used for in your project?** To show the intensity of crimes across two dimensions, like Hour of Day vs Day of Week.
14. **What is Correlation?** A measure of how two numerical variables move together.
15. **Why did you use Spearman correlation instead of Pearson?** Because my geographic identifiers (District, Ward) are ordinal/categorical numbers, not continuous linear scales. Spearman ranks data, handling non-linear relationships better.
16. **Does correlation imply causation?** No. District and Ward correlate because they overlap geographically, not because a Ward "causes" a District.
17. **What is an Outlier?** A data point far removed from the rest of the distribution.
18. **How did you detect outliers?** Using the IQR method. Any value outside Q1-1.5*IQR and Q3+1.5*IQR was flagged.
19. **Did you remove outliers?** No. In spatial data, an extreme latitude just means a crime on the edge of town, which is a valid event.
20. **What is a Chi-Square test?** A statistical test used to determine if two categorical variables (like Crime Type and Arrest) are independent or related.
21. **What does a p-value < 0.05 mean in your Chi-Square test?** It means the probability that the relationship we observe is due to random chance is less than 5%. We reject the null hypothesis and conclude Crime Type affects Arrests.
22. **What is Cramer's V?** It measures the strength of association between categorical variables after a Chi-square test proves a relationship exists.
23. **Why did you use Point-Biserial correlation?** To test the relationship between a continuous variable (Hour) and a binary variable (Arrest).
24. **What was the peak time for crime?** Noon (12:00 PM).
25. **Did seasonality affect crime?** Yes, Summer had higher incident volumes than Winter.
26. **What does `pd.crosstab` do?** It creates a frequency table showing the counts of combinations of two categorical variables.
27. **Why use a donut chart instead of a pie chart for arrests?** It's mostly an aesthetic choice, it can be easier to read the proportions and allows for a label in the center.
28. **If you built a Machine Learning model, what would you predict?** Whether an incident results in an Arrest.
29. **What challenge would you face predicting arrests?** Class imbalance, because the vast majority of crimes do not result in an arrest.
30. **What is the most surprising insight you found?** (Your subjective answer based on the findings, e.g., how low the overall arrest rate is).

---

## 17. Beginner-Friendly Final Explanation

**The 30-Second Pitch (For the Professor's quick question):**
"I took 120,000 raw Chicago police records and built an automated EDA pipeline. I cleaned mixed date formats and faulty coordinates, engineered temporal features like Day of Week and Season, and used statistical tests like Chi-Square to prove that arrest rates are heavily dependent on crime type and location. Finally, I visualized all these patterns into an executive dashboard, showing that crime peaks at noon, heavily concentrates in Summer, and is dominated by Theft and Battery."

**The 5-Minute Story:**
"Imagine getting a giant spreadsheet of every crime in Chicago. It’s too big to read row by row. My goal was to make the data tell a story.

First, I had to **understand and clean** the data. I realized the dates were entered in two different formats, so I wrote custom code to standardize them. I also found errors where coordinates were marked as '0,0' (which is the ocean), so I blanked those out to fix my maps.

Once the data was clean, I did **Feature Engineering**. A raw timestamp isn't helpful, so I ripped it apart to extract the Hour, the Day of the Week, and the Season. This let me ask questions like 'what happens on weekends?'.

Next came **Univariate Analysis**—looking at one thing at a time. I counted up the crime types and found that Theft and Battery are by far the most common. I mapped the times and found that crime strangely peaks at noon, and Summer is much worse than Winter.

Then I did **Bivariate Analysis**—comparing two things. I wanted to know who gets arrested. I found that if you commit a Narcotics crime, you are almost certainly getting arrested, but if you steal a car (Motor Vehicle Theft), an arrest is extremely rare.

I didn't just want to guess, so I used **Statistical Tests** like Chi-Square to mathematically prove that things like 'Crime Type' and 'Arrest' are strongly linked, and it wasn't just random chance in the data.

Finally, I compiled all the most important charts—bar charts, line trends, and geographic heatmaps—into a single **Summary Dashboard** so anyone can look at it and instantly understand the landscape of Chicago crime, preparing the dataset perfectly if we ever want to train a Machine Learning model to predict arrests."
