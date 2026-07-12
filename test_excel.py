import pandas as pd

df = pd.read_excel("samples/sample.xlsx", engine="openpyxl")

print(df)