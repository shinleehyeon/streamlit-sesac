from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.set_page_config(page_title="HR 퇴직 현황 대시보드", layout="wide")
st.title("HR 퇴직 현황 대시보드")
st.caption("HR Data.csv · 사이드바 필터 + KPI + 핵심 퇴직률 그래프")

DATA_PATH = Path(__file__).parent / "HR Data.csv"


@st.cache_data
def load_hr() -> pd.DataFrame:
    hr = pd.read_csv(DATA_PATH)
    hr["퇴직"] = hr["퇴직여부"].map({"No": 0, "Yes": 1}).astype("int8")
    hr["상태"] = hr["퇴직여부"].map({"No": "재직", "Yes": "퇴직"})

    hr["연령대"] = pd.cut(
        hr["나이"],
        bins=[0, 29, 39, 49, 59, 100],
        labels=["20대 이하", "30대", "40대", "50대", "60대 이상"],
    )
    hr["근속구간"] = pd.cut(
        hr["근속연수"],
        bins=[-1, 2, 5, 10, 100],
        labels=["2년 이하", "3~5년", "6~10년", "11년 이상"],
    )
    hr["월급여구간"] = pd.qcut(
        hr["월급여"],
        q=4,
        labels=["하위 25%", "25~50%", "50~75%", "상위 25%"],
    )
    return hr


def attrition_by(df: pd.DataFrame, col: str) -> pd.DataFrame:
    result = (
        df.groupby(col, observed=False)
        .agg(
            직원수=("퇴직", "size"),
            퇴직자수=("퇴직", "sum"),
            퇴직률=("퇴직", "mean"),
        )
        .reset_index()
    )
    result["퇴직률"] = (result["퇴직률"] * 100).round(1)
    return result


def draw_rate_chart(data: pd.DataFrame, x: str, y: str, title: str, baseline: float, horizontal: bool = False):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    if len(data):
        if horizontal:
            sns.barplot(data=data, y=y, x=x, ax=ax, color="#4C78A8")
            ax.axvline(baseline, color="red", linestyle="--", label="전체 퇴직률")
            ax.set_xlabel("퇴직률(%)")
        else:
            sns.barplot(data=data, x=x, y=y, ax=ax, color="#4C78A8")
            ax.axhline(baseline, color="red", linestyle="--", label="전체 퇴직률")
            ax.set_ylabel("퇴직률(%)")
            ax.tick_params(axis="x", rotation=15)
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    st.pyplot(fig)
    plt.close(fig)


hr = load_hr()

# ── 사이드바 필터 ─────────────────────────────────────────────
st.sidebar.header("조회 조건")

department = st.sidebar.selectbox(
    "부서",
    ["전체", *sorted(hr["부서"].dropna().unique())],
)
status = st.sidebar.multiselect(
    "재직 상태",
    ["재직", "퇴직"],
    default=["재직", "퇴직"],
)
overtime = st.sidebar.multiselect(
    "야근 여부",
    sorted(hr["야근정도"].dropna().unique()),
    default=sorted(hr["야근정도"].dropna().unique()),
)
age_group = st.sidebar.multiselect(
    "연령대",
    ["20대 이하", "30대", "40대", "50대", "60대 이상"],
    default=["20대 이하", "30대", "40대", "50대", "60대 이상"],
)
min_tenure = st.sidebar.slider(
    "최소 근속연수",
    min_value=int(hr["근속연수"].min()),
    max_value=int(hr["근속연수"].max()),
    value=0,
)

# 필터 적용
result = hr[hr["근속연수"] >= min_tenure].copy()
if department != "전체":
    result = result[result["부서"] == department]
if status:
    result = result[result["상태"].isin(status)]
if overtime:
    result = result[result["야근정도"].isin(overtime)]
if age_group:
    result = result[result["연령대"].isin(age_group)]

# KPI는 "필터된 집단" 기준, 기준선은 전체 회사 퇴직률
total_employees = len(result)
total_attritions = int(result["퇴직"].sum()) if total_employees else 0
filtered_rate = (total_attritions / total_employees * 100) if total_employees else 0.0
overall_rate = hr["퇴직"].mean() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("전체 직원 수", f"{total_employees:,}명")
k2.metric("퇴직자 수", f"{total_attritions:,}명")
k3.metric("선택 집단 퇴직률", f"{filtered_rate:.1f}%")
k4.metric("전체 퇴직률(기준)", f"{overall_rate:.1f}%")

st.divider()

# ── 그래프 4개만 ── (노트북 6개 중 핵심만)
department_result = attrition_by(result, "부서") if len(result) else pd.DataFrame()
age_result = attrition_by(result, "연령대") if len(result) else pd.DataFrame()
tenure_result = attrition_by(result, "근속구간") if len(result) else pd.DataFrame()
overtime_result = attrition_by(result, "야근정도") if len(result) else pd.DataFrame()

c1, c2 = st.columns(2)
with c1:
    draw_rate_chart(
        department_result, x="퇴직률", y="부서", title="부서별 퇴직률",
        baseline=overall_rate, horizontal=True,
    )
with c2:
    draw_rate_chart(
        age_result, x="연령대", y="퇴직률", title="연령대별 퇴직률",
        baseline=overall_rate,
    )

c3, c4 = st.columns(2)
with c3:
    draw_rate_chart(
        tenure_result, x="근속구간", y="퇴직률", title="근속구간별 퇴직률",
        baseline=overall_rate,
    )
with c4:
    draw_rate_chart(
        overtime_result, x="야근정도", y="퇴직률", title="야근 여부별 퇴직률",
        baseline=overall_rate,
    )

st.caption("빨간 점선 = 전체 회사 퇴직률 기준선 · 그래프는 현재 필터 결과 기준")

# 테이블
st.subheader("직원 목록")
show = result[
    ["직원ID", "상태", "나이", "연령대", "부서", "야근정도", "출장빈도", "월급여", "근속연수", "근속구간", "월급여구간"]
].sort_values(["부서", "직원ID"]).reset_index(drop=True)
st.dataframe(show, use_container_width=True, hide_index=True, height=360)
