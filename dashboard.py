import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="가공식품 건강 분석",
    page_icon="🍔",
    layout="wide"
)

st.markdown("""
<style>

.main {
    background-color: #F8FAFC;
}

div[data-testid="metric-container"] {
    background-color: white;
    border: 2px solid #E5E7EB;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

div[data-testid="stSidebar"] {
    background-color: #F1F5F9;
}

</style>
""", unsafe_allow_html=True)

# 한글 폰트
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# -------------------------
# 페이지 제목
# -------------------------

st.markdown("""
# 🍔 가공식품 건강 분석 AI 대시보드

### 식품의약품안전처 영양성분 데이터를 기반으로 건강도를 분석합니다.

---
""")

st.info("""
📌 프로젝트 개요

식품의약품안전처 영양성분 데이터를 활용하여
가공식품의 건강도를 분석하고 건강점수를 제공합니다.
""")
# -------------------------
# 데이터 불러오기
# -------------------------

df = pd.read_excel(
    "식품의약품안전처_가공식품 품목별 영양성분 DB_20221231.xlsx"
)

df.columns = df.columns.str.replace('\n', '').str.strip()

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

# -------------------------
# 건강점수 함수
# -------------------------

def health_score(row):

    score = 100

    kcal = row['에너지(kcal)']
    carb = row['탄수화물(g)']
    protein = row['단백질(g)']
    fat = row['지방(g)']
    sodium = row['나트륨(mg)']
    sugar = row['당류(g)']

    # 칼로리
    if kcal > 1000:
        score -= 10
    elif kcal > 800:
        score -= 5

    # 탄수화물
    if 40 <= carb <= 80:
        score += 3
    elif carb > 120:
        score -= 5

    # 단백질
    if protein < 10:
        score -= 5
    elif protein < 20:
        score += 5
    elif protein < 30:
        score += 10
    else:
        score += 15

    # 지방
    if 10 <= fat <= 20:
        score += 3
    elif 30 <= fat <= 40:
        score -= 5
    elif fat > 40:
        score -= 10

    # 나트륨
    if sodium <= 500:
        score += 5
    elif sodium <= 1000:
        pass
    elif sodium <= 1500:
        score -= 10
    else:
        score -= 20

    # 당류
    if sugar <= 10:
        score += 3
    elif sugar <= 20:
        pass
    elif sugar <= 35:
        score -= 5
    else:
        score -= 15

    return score


df['건강점수'] = df.apply(health_score, axis=1)


st.sidebar.header("🏆 건강식품 랭킹")

st.sidebar.markdown("""
가공식품 건강점수 상위 10개를
확인할 수 있습니다.
""")

top10 = (
    df[['가공식품품목명', '건강점수']]
    .sort_values(
        by='건강점수',
        ascending=False
    )
    .head(10)
)

st.sidebar.dataframe(
    top10,
    use_container_width=True
)

# -------------------------
# 식품 선택
# -------------------------

food = st.selectbox(
    "식품을 선택하세요",
    sorted(df["가공식품품목명"].unique())
)

selected = df[df["가공식품품목명"] == food].iloc[0]

score = selected['건강점수']

avg_score = round(df['건강점수'].mean(), 1)

difference = round(score - avg_score, 1)

# -------------------------
# 건강등급
# -------------------------

if score >= 115:
    grade = "🟢 A (매우 건강)"
elif score >= 100:
    grade = "🟡 B (건강)"
elif score >= 90:
    grade = "🟠 C (보통)"
else:
    grade = "🔴 D (주의)"
# -------------------------
# 점수 표시
# -------------------------

col1, col2, col3 = st.columns(3)
st.divider()

with col1:
    st.metric(
        "건강점수",
        f"{score}점"
    )

with col2:
    st.metric(
        "건강등급",
        grade
    )

with col3:
    st.metric(
        "평균 대비",
        f"{difference:+.1f}점"
    )
    
st.subheader("📈 건강도")

health_ratio = min(score / 130, 1.0)

st.progress(health_ratio)

if score >= 115:
    st.success("🟢 매우 건강한 식품입니다.")

elif score >= 100:
    st.info("🔵 건강한 식품입니다.")

elif score >= 90:
    st.warning("🟠 보통 수준의 식품입니다.")

else:
    st.error("🔴 섭취 시 주의가 필요합니다.")
    
# -------------------------
# 영양성분 정보
# -------------------------

st.subheader(f"📌 {food}")

left, right = st.columns(2)

with left:

    nutrition_df = pd.DataFrame(
        {
            "영양성분": [
                "칼로리",
                "단백질",
                "지방",
                "탄수화물",
                "당류",
                "나트륨"
            ],
            "값": [
                f"{selected['에너지(kcal)']} kcal",
                f"{selected['단백질(g)']} g",
                f"{selected['지방(g)']} g",
                f"{selected['탄수화물(g)']} g",
                f"{selected['당류(g)']} g",
                f"{selected['나트륨(mg)']} mg"
            ]
        }
    )

    st.markdown("### 📋 영양성분 정보")
    st.caption("선택한 식품의 영양성분 요약")

    st.dataframe(
        nutrition_df,
        use_container_width=True,
        hide_index=True
    )

with right:

    graph_df = pd.DataFrame(
        {
            "영양소": [
                "단백질",
                "지방",
                "탄수화물",
                "당류"
            ],
            "함량(g)": [
                selected["단백질(g)"],
                selected["지방(g)"],
                selected["탄수화물(g)"],
                selected["당류(g)"]
            ]
        }
    )

    st.markdown("### 📊 영양성분 비교")
    st.caption("주요 영양성분 함량 비교")

    graph_df = pd.DataFrame(
        {
            "영양소": [
                "단백질",
                "지방",
                "탄수화물",
                "당류"
            ],
            "함량": [
                selected["단백질(g)"],
                selected["지방(g)"],
                selected["탄수화물(g)"],
                selected["당류(g)"]
            ]
        }
    )
    
    st.bar_chart(
    graph_df.set_index("영양소")
    )

# -------------------------
# AI 분석
# -------------------------

st.subheader("🤖 AI 건강 분석 결과")

analysis = f"""
**{food}**의 건강점수는 **{score}점**입니다.

• 탄수화물 : {selected['탄수화물(g)']} g  
• 단백질 : {selected['단백질(g)']} g  
• 지방 : {selected['지방(g)']} g  
• 당류 : {selected['당류(g)']} g  
• 나트륨 : {selected['나트륨(mg)']} mg

"""

if selected['당류(g)'] > 20:
    analysis += "\n⚠️ 당류 함량이 높아 과다 섭취에 주의가 필요합니다.\n"

if selected['나트륨(mg)'] > 1000:
    analysis += "\n⚠️ 나트륨 함량이 높아 건강점수에 불리하게 작용했습니다.\n"

if selected['단백질(g)'] >= 20:
    analysis += "\n✅ 단백질 함량이 높아 영양적으로 우수합니다.\n"

if selected['탄수화물(g)'] > 80:
    analysis += "\n⚠️ 탄수화물 함량이 높아 적정량 섭취를 권장합니다.\n"

if (
    selected['당류(g)'] <= 10
    and selected['나트륨(mg)'] <= 500
):
    analysis += "\n✅ 당류와 나트륨 함량이 낮아 비교적 건강한 식품으로 평가됩니다.\n"

st.success(analysis)

