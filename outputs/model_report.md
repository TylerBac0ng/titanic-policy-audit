# Model Report

Framing: evacuation-triage classifier — see problem_statement.md.

## Logistic Regression
- Accuracy: 80.4%
- Recall (survived): 72.5%
- ROC-AUC: 0.853
```
              precision    recall  f1-score   support

        Died       0.83      0.85      0.84       110
    Survived       0.76      0.72      0.74        69

    accuracy                           0.80       179
   macro avg       0.79      0.79      0.79       179
weighted avg       0.80      0.80      0.80       179
```

## Random Forest
- Accuracy: 79.9%
- Recall (survived): 68.1%
- ROC-AUC: 0.833
```
              precision    recall  f1-score   support

        Died       0.81      0.87      0.84       110
    Survived       0.77      0.68      0.72        69

    accuracy                           0.80       179
   macro avg       0.79      0.78      0.78       179
weighted avg       0.80      0.80      0.80       179
```

## Fairness audit (Logistic Regression, chosen by ROC-AUC)

Recall (true positive rate) by group — a gap here means the model is better at correctly flagging survivors in one group than another, which for this dataset reflects structural access (class/deck), not individual risk. Report this alongside accuracy, don't hide it.

| Pclass | n | Recall (TPR) |
|---|---|---|
| 1 | 46 | 68.0% |
| 2 | 34 | 90.0% |
| 3 | 99 | 62.5% |

| Sex | n | Recall (TPR) |
|---|---|---|
| female | 63 | 100.0% |
| male | 116 | 24.0% |
