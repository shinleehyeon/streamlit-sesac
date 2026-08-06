from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.set_page_config(page_title="HR 퇴직 현황 대시보드", layout="wide")
st.title("HR 퇴직 현황 대시보드")

DATA_PATH = Path(__file__).parent / "HR Data.csv"


@st.cache_data
def load_hr():
    hr = pd.read_csv(DATA_PATH)
    hr["퇴직"] = hr["퇴직여부"].map({"No": 0, "Yes": 1})
    hr["연령대"] = pd.cut(
        hr["나이"], bins=[0, 29, 39, 49, 59, 100],
        labels=["20대 이하", "30대", "40대", "50대", "60대 이상"],
    )
    hr["근속구간"] = pd.cut(
        hr["근속연수"], bins=[-1, 2, 5, 10, 100],
        labels=["2년 이하", "3~5년", "6~10년", "11년 이상"],
    )
    return hr


def attrition_by(df, col):
    out = (
        df.groupby(col, observed=False)
        .agg(직원수=("퇴직", "size"), 퇴직률=("퇴직", "mean"))
        .reset_index()
    )
    out["퇴직률"] = (out["퇴직률"] * 100).round(1)
    return out


def draw_bar(data, x, baseline, title, horizontal=False):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    if len(data):
        if horizontal:
            sns.barplot(data=data, y=x, x="퇴직률", ax=ax)
            ax.axvline(baseline, color="red", linestyle="--", label="전체 퇴직률")
            ax.set(title=title, xlabel="퇴직률(%)")
        else:
            sns.barplot(data=data, x=x, y="퇴직률", ax=ax)
            ax.axhline(baseline, color="red", linestyle="--", label="전체 퇴직률")
            ax.set(title=title, ylabel="퇴직률(%)")
            ax.tick_params(axis="x", rotation=15)
        ax.legend()
    st.pyplot(fig)
    plt.close(fig)


hr = load_hr()

st.sidebar.header("조회 조건")
department = st.sidebar.selectbox("부서", ["전체", *sorted(hr["부서"].unique())])
min_tenure = st.sidebar.slider("최소 근속연수", int(hr["근속연수"].min()), int(hr["근속연수"].max()), 0)

result = hr[hr["근속연수"] >= min_tenure]
if department != "전체":
    result = result[result["부서"] == department]

n, left = len(result), int(result["퇴직"].sum())
rate = left / n * 100 if n else 0.0
baseline = hr["퇴직"].mean() * 100

c1, c2, c3 = st.columns(3)
c1.metric("전체 직원 수", f"{n:,}명")
c2.metric("퇴직자 수", f"{left:,}명")
c3.metric("선택 집단 퇴직률", f"{rate:.1f}%")
st.divider()

left_col, right_col = st.columns(2)
with left_col:
    draw_bar(attrition_by(result, "부서"), "부서", baseline, "부서별 퇴직률", horizontal=True)
    draw_bar(attrition_by(result, "근속구간"), "근속구간", baseline, "근속구간별 퇴직률")
with right_col:
    draw_bar(attrition_by(result, "연령대"), "연령대", baseline, "연령대별 퇴직률")
    draw_bar(attrition_by(result, "야근정도"), "야근정도", baseline, "야근 여부별 퇴직률")
