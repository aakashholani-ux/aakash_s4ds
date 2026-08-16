# Model Comparison

| Model | CV Accuracy | CV Precision | CV Recall | CV F1 | CV ROC-AUC | Test Accuracy | Test Precision | Test Recall | Test F1 | Test ROC-AUC | PR-AUC |
| ----- | ----------: | -----------: | --------: | ----: | ---------: | ------------: | -------------: | ----------: | ------: | -----------: | -----: |
| Logistic Regression | 0.7596 | 0.6106 | 0.7383 | 0.6684 | 0.8449 | 0.7578 | 0.6092 | 0.7298 | 0.6641 | 0.8404 | 0.7594 |
| Random Forest | 0.7761 | 0.6472 | 0.6999 | 0.6722 | 0.8494 | 0.7765 | 0.6535 | 0.6785 | 0.6658 | 0.8420 | 0.7638 |

## Evaluation
- Both models perform reasonably well, but the **Random Forest** likely achieved a higher ROC-AUC and PR-AUC.
- The use of `class_weight='balanced'` ensures that we don't just predict the majority class (No Arrest).
- There is minimal evidence of overfitting for Logistic Regression as CV and Test metrics match closely. Random Forest may show slight overfitting but generally generalizes better on nonlinear relationships.
- ROC-AUC and PR-AUC are most important given the 67/33 class imbalance.
