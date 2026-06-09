import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
     
df = pd.read_excel("식품의약품안전처_가공식품 품목별 영양성분 DB_20221231.xlsx")

df.columns = df.columns.str.replace('\n', '')

print(df.head())
print(df.columns)

df = df[
    [
        '가공식품품목명',
        '식품중분류명',
        '에너지(kcal)',
        '단백질(g)',
        '지방(g)',
        '탄수화물(g)',
        '당류(g)',
        '나트륨(mg)'
    ]
]

numeric_cols = [
    '에너지(kcal)',
    '단백질(g)',
    '지방(g)',
    '탄수화물(g)',
    '당류(g)',
    '나트륨(mg)'
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna()

print(df.head())

def health_score(row):

    score = 100

    # 칼로리
    kcal = row['에너지(kcal)']

    if kcal > 1000:
        score -= 10
    elif kcal > 800:
        score -= 5

    # 탄수화물
    carb = row['탄수화물(g)']

    if 40 <= carb <= 80:
        score += 3
    elif carb > 120:
        score -= 5

    # 단백질
    protein = row['단백질(g)']

    if protein < 10:
        score -= 5
    elif protein < 20:
        score += 5
    elif protein < 30:
        score += 10
    else:
        score += 15

    # 지방
    fat = row['지방(g)']

    if 10 <= fat <= 20:
        score += 3
    elif 30 <= fat <= 40:
        score -= 5
    elif fat > 40:
        score -= 10

    # 나트륨
    sodium = row['나트륨(mg)']

    if sodium <= 500:
        score += 5
    elif sodium <= 1000:
        score += 0
    elif sodium <= 1500:
        score -= 10
    else:
        score -= 20

    # 당류
    sugar = row['당류(g)']

    if sugar <= 10:
        score += 3
    elif sugar <= 20:
        score += 0
    elif sugar <= 35:
        score -= 5
    else:
        score -= 15

    return score

df['건강점수'] = df.apply(
    health_score,
    axis=1
)

print(
    df[
        ['가공식품품목명', '건강점수']
    ].head(20)
)

top10 = df.sort_values(
    '건강점수',
    ascending=False
).head(10)

plt.figure(figsize=(10,5))

plt.bar(
    top10['가공식품품목명'],
    top10['건강점수']
)

plt.xticks(rotation=90)
plt.title('건강점수 TOP10')
plt.tight_layout()

plt.show()