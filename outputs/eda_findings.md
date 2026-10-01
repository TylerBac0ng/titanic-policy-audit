# EDA Findings

## Overall
Overall survival rate: 38.3% (341 of 891 passengers).

## Sex
Female survival rate: 73.9%. Male survival rate: 18.9%.

## Pclass
Pclass
1    63.0%
2    47.3%
3    24.0%

## Pclass x Sex
Sex    female   male
Pclass              
1       96.8%  36.9%
2       92.1%  15.7%
3       49.3%  13.5%

## Age
Survival rate for age <= 10: 59.4% vs overall 38.3%.
Age was imputed for 177 passengers (median by Pclass+Sex); interpret age-based patterns with that in mind.

## Fare
Median fare, survived: $26.00. Median fare, did not survive: $10.50. 15 passengers paid $0 (kept as-is, noted as an anomaly).

## Family size
Alone (1)      30.2%
Small (2-4)    57.9%
Large (5+)     16.1%

## Title
Title
Mrs       79.4%
Miss      69.7%
Master    57.5%
Rare      34.8%
Mr        15.7%

## Deck
Deck
A          46.7%
B          74.5%
C          59.3%
D          75.8%
E          75.0%
F          61.5%
G          50.0%
Unknown    29.8%
Note: 'Unknown' deck is 77% of passengers and correlates with lower Pclass.

## Correlation with Survived (numeric features only; Sex is categorical and excluded here)
Pclass_num    -0.34
Age           -0.06
SibSp         -0.03
FamilySize     0.02
Parch          0.08
Fare           0.26
