import pandas as pd

data = pd.read_excel("NF.xlsx", header=None) 
print(data.head()) # 상위 5개 데이터 미리보기
data1 = pd.read_excel("SF.xlsx", header=None)
print(data1)
data2 = pd.read_excel("SD.xlsx", header=None)
print(data2)