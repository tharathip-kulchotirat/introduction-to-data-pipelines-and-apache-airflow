import pandas as pd

df = pd.read_csv('titanic.csv')

# using df.info to check null value
print(df.info())

# Calculate Data Quality of every cols using null value count
dqs = []
for col in df.columns:
    not_null = df[col].notnull()
    dq = not_null.sum() / not_null.shape[0]
    print(f"Data Quality of {col}: " , dq)
    dqs.append(dq)

print('Completeness of the dataset: ', sum(dqs) / len(dqs))
