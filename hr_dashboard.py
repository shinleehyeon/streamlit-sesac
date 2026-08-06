from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.set_page_config(page_title="HR 대시보드", page_icon="◈", layout="wide")
st.title("HR 대시보드")
st.caption("HR Data.csv 기준으로 인원·퇴직·급여 현황을 조회합니다.")

DATA_PATH = Path(__file__).parent / "HR Data.csv"

DEPT_KO = {
    "Human Resources": "인사",
    "Research & Development": "연구개발",
    "Sales": "영업",
}
ATTRITION_KO = {"No": "재직", "Yes": "퇴직"}
GENDER_KO = {"Male": "남", "Female": "여"}
TRAVEL_KO = {
    "Non-Travel": "출장없음",
    "Travel_Rarely": "가끔",
    "Travel_Frequently": "자주",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    raw = pd.read_csv(DATA_PATH)
    df = raw.copy()
    df["부서_표시"] = df["부서"].map(DEPT_KO).fillna(df["부서"])
    df["상태"] = df["퇴직여부"].map(ATTRITION_KO).fillna(df["퇴직여부"])
    df["성별_표시"] = df["성별"].map(GENDER_KO).fillna(df["성별"])
    df["출장_표시"] = df["출장빈도"].map(TRAVEL_KO).fillna(df["출장빈도"])
    return df


df = load_data()

# 사이드바 필터
st.sidebar.header("조회 조건")
department = st.sidebar.selectbox("부서", ["전체", *sorted(df["부서_표시"].unique())])
status = st.sidebar.multiselect(
    "재직 상태",
    ["재직", "퇴직"],
    default=["재직", "퇴직"],
)
gender = st.sidebar.multiselect(
    "성별",
    ["남", "여"],
    default=["남", "여"],
)
min_tenure = st.sidebar.slider(
    "최소 근속연수",
    min_value=int(df["근속연수"].min()),
    max_value=int(df["근속연수"].max()),
    value=0,
    step=1,
)
min_salary = st.sidebar.slider(
    "최소 월급여",
    min_value=int(df["월급여"].min()),
    max_value=int(df["월급여"].max()),
    value=int(df["월급여"].min()),
    step=500,
)

# 필터링
result = df[
    (df["근속연수"] >= min_tenure)
    & (df["월급여"] >= min_salary)
].copy()
if department != "전체":
    result = result[result["부서_표시"] == department]
if status:
    result = result[result["상태"].isin(status)]
if gender:
    result = result[result["성별_표시"].isin(gender)]

# KPI
employee_count = len(result)
active_count = int((result["상태"] == "재직").sum())
attrition_count = int((result["상태"] == "퇴직").sum())
attrition_rate = (attrition_count / employee_count * 100) if employee_count else 0.0
avg_salary = float(result["월급여"].mean()) if employee_count else 0.0
avg_tenure = float(result["근속연수"].mean()) if employee_count else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("전체 인원", f"{employee_count:,}명")
k2.metric("재직", f"{active_count:,}명")
k3.metric("퇴직", f"{attrition_count:,}명", delta=f"퇴직률 {attrition_rate:.1f}%")
k4.metric("평균 월급여", f"${avg_salary:,.0f}", delta=f"평균 근속 {avg_tenure:.1f}년")

st.divider()

# 그래프
graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    st.subheader("부서별 인원")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    if len(result):
        dept_count = (
            result.groupby("부서_표시", observed=True)
            .size()
            .reset_index(name="인원")
            .sort_values("인원", ascending=False)
        )
        sns.barplot(data=dept_count, x="부서_표시", y="인원", ax=ax1, color="#1a6b5c")
    ax1.set_xlabel("부서")
    ax1.set_ylabel("인원(명)")
    ax1.set_ylim(bottom=0)
    st.pyplot(fig1)
    plt.close(fig1)

with graph_col2:
    st.subheader("재직 / 퇴직 분포")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    if len(result):
        status_count = (
            result.groupby("상태", observed=True)
            .size()
            .reindex(["재직", "퇴직"], fill_value=0)
            .reset_index(name="인원")
        )
        sns.barplot(data=status_count, x="상태", y="인원", ax=ax2, color="#c45c26")
    ax2.set_xlabel("상태")
    ax2.set_ylabel("인원(명)")
    ax2.set_ylim(bottom=0)
    st.pyplot(fig2)
    plt.close(fig2)

# 추가 그래프
g3, g4 = st.columns(2)

with g3:
    st.subheader("부서별 평균 월급여")
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    if len(result):
        salary_by_dept = (
            result.groupby("부서_표시", observed=True)["월급여"]
            .mean()
            .reset_index()
            .sort_values("월급여", ascending=False)
        )
        sns.barplot(data=salary_by_dept, x="부서_표시", y="월급여", ax=ax3, color="#2f6fed")
    ax3.set_xlabel("부서")
    ax3.set_ylabel("평균 월급여")
    ax3.set_ylim(bottom=0)
    st.pyplot(fig3)
    plt.close(fig3)

with g4:
    st.subheader("성별 인원")
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    if len(result):
        gender_count = (
            result.groupby("성별_표시", observed=True)
            .size()
            .reindex(["남", "여"], fill_value=0)
            .reset_index(name="인원")
        )
        sns.barplot(data=gender_count, x="성별_표시", y="인원", ax=ax4, color="#7a5af8")
    ax4.set_xlabel("성별")
    ax4.set_ylabel("인원(명)")
    ax4.set_ylim(bottom=0)
    st.pyplot(fig4)
    plt.close(fig4)

# 테이블
st.subheader("직원 목록")
show_cols = [
    "직원ID",
    "상태",
    "나이",
    "성별_표시",
    "부서_표시",
    "전공",
    "결혼여부",
    "월급여",
    "근속연수",
    "업무만족도",
    "야근정도",
    "출장_표시",
]
table = (
    result[show_cols]
    .rename(
        columns={
            "성별_표시": "성별",
            "부서_표시": "부서",
            "출장_표시": "출장빈도",
        }
    )
    .sort_values(["부서", "직원ID"])
    .reset_index(drop=True)
)
st.dataframe(table, use_container_width=True, hide_index=True, height=420)
st.caption(f"총 {len(table):,}명 · 데이터 출처: HR Data.csv")
