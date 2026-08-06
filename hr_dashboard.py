from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.set_page_config(
    page_title="HR 퇴직 현황 대시보드",
    page_icon=":bar_chart:",
    layout="wide",
)

DATA_PATH = Path(__file__).parent / "HR Data.csv"


@st.cache_data
def load_hr():
    hr = pd.read_csv(DATA_PATH)
    hr["퇴직"] = hr["퇴직여부"].map({"No": 0, "Yes": 1})
    hr["상태"] = hr["퇴직여부"].map({"No": "재직", "Yes": "퇴직"})
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


def show(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def draw(kind, data, *, col=None, baseline=None, title=""):
    fig, ax = plt.subplots(figsize=(6, 3.8))
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")
    if not len(data):
        show(fig)
        return

    main, danger, soft = "cornflowerblue", "salmon", "skyblue"

    if kind == "stacked":
        ct = (
            data.groupby(["부서", "상태"], observed=False).size()
            .unstack(fill_value=0).reindex(columns=["재직", "퇴직"], fill_value=0)
        )
        ct.plot(kind="bar", stacked=True, ax=ax, color=["cornflowerblue", "salmon"], width=0.7)
        ax.set(title=title, xlabel="부서", ylabel="인원(명)")
        ax.tick_params(axis="x", rotation=15)
        ax.legend(title="상태")

    elif kind == "line":
        sns.lineplot(data=data, x=col, y="퇴직률", marker="o", color=main,
                     linewidth=2.2, markersize=9, ax=ax)
        ax.axhline(baseline, color=danger, linestyle="--", label="전체 퇴직률")
        ax.set(title=title, ylabel="퇴직률(%)", ylim=(0, None))
        ax.legend()

    elif kind == "lollipop":
        y, x = data[col].astype(str), data["퇴직률"]
        ax.hlines(y=y, xmin=0, xmax=x, color=soft, linewidth=3)
        ax.plot(x, y, "o", color=main, markersize=11)
        ax.axvline(baseline, color=danger, linestyle="--", label="전체 퇴직률")
        ax.set(title=title, xlabel="퇴직률(%)", xlim=(0, None))
        ax.legend()

    elif kind == "bar":
        sns.barplot(data=data, x=col, y="퇴직률", ax=ax, color=main)
        ax.axhline(baseline, color=danger, linestyle="--", label="전체 퇴직률")
        ax.set(title=title, ylabel="퇴직률(%)")
        ax.legend()

    ax.tick_params(colors="lightgray")
    ax.xaxis.label.set_color("lightgray")
    ax.yaxis.label.set_color("lightgray")
    ax.title.set_color("white")
    for spine in ax.spines.values():
        spine.set_color("gray")
    show(fig)


hr = load_hr()
baseline = hr["퇴직"].mean() * 100

cols = st.columns([1, 3], gap="large")
filter_panel = cols[0].container(border=True)

with filter_panel:
    st.markdown("**Filters**")
    department = st.selectbox("부서", ["전체", *sorted(hr["부서"].unique())])
    min_tenure = st.slider(
        "최소 근속연수",
        int(hr["근속연수"].min()),
        int(hr["근속연수"].max()),
        0,
    )
    st.caption(f"전체 퇴직률 기준: {baseline:.1f}%")

result = hr[hr["근속연수"] >= min_tenure]
if department != "전체":
    result = result[result["부서"] == department]

n = len(result)
attritions = int(result["퇴직"].sum())
rate = attritions / n * 100 if n else 0.0

with cols[1]:
    st.header("Overview", divider="gray")
    ""
    k1, k2, k3 = st.columns(3)
    k1.metric(label="전체 직원 수", value=f"{n:,}명")
    k2.metric(label="퇴직자 수", value=f"{attritions:,}명")
    k3.metric(label="선택 집단 퇴직률", value=f"{rate:.1f}%")

    ""
    st.header("Charts", divider="gray")
    ""
    left_col, right_col = st.columns(2)
    with left_col:
        draw("stacked", result, title="부서별 재직·퇴직 인원")
        draw("lollipop", attrition_by(result, "근속구간"), col="근속구간",
             baseline=baseline, title="근속구간별 퇴직률")
    with right_col:
        draw("line", attrition_by(result, "연령대"), col="연령대",
             baseline=baseline, title="연령대별 퇴직률")
        draw("bar", attrition_by(result, "야근정도"), col="야근정도",
             baseline=baseline, title="야근 여부별 퇴직률")