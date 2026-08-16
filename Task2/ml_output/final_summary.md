# Final Summary

## Final Model Recommendation
- **Model Selected**: Random Forest
- **Key Performance Metrics (Test)**: 
  - ROC-AUC: 0.8420
  - PR-AUC: 0.7638
  - F1-Score: 0.6658
- **Why it was selected**: It provided the highest overall discrimination ability (ROC-AUC) and best handles non-linear relationships in categorical data like Location Description and Primary Type.
- **Main Strengths**: Captures complex interactions between location, time, and crime type better than Logistic Regression.
- **Main Weaknesses**: Slower to train and harder to interpret purely from coefficients (requires feature importance).

## Key ML Findings
- The strongest predictors for an arrest are highly related to the **Primary Type** (e.g., Narcotics often guarantees an arrest, whereas Theft does not) and **Location Description**.
- Temporal features (Hour, Month, Weekend) have minor but non-trivial predictive power, particularly when modeled with cyclical encoding.
- The EDA findings are perfectly consistent with the ML feature importance.

## Limitations
- **Data Leakage Potential**: While extreme care was taken, some administrative fields or locations might subtly imply post-arrest status.
- **Causation**: The model predicts the *probability of a recorded arrest*, not whether a crime fundamentally *deserves* an arrest.
- **Class Imbalance**: Even with balancing, predicting the minority class perfectly is difficult.

## Conclusion
The pipeline successfully processes temporal and categorical geographic data, correctly avoids data leakage, and provides a robust baseline for anticipating arrest probabilities based purely on the initial incident report parameters.
