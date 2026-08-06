import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

st.set_page_config(page_title="HR 대시보드", page_icon="◈", layout="wide")
st.title("HR 대시보드")
st.caption("부서·상태 기준으로 인원 현황을 조회합니다.")

# 1. 데이터 만들기
df = pd.DataFrame(
    {
        "사번": [f"E{2024000 + i}" for i in range(12)],
        "이름": [
            "김민수", "이영희", "박철수", "최지수", "정하늘", "한유진",
            "오세훈", "윤서아", "장도윤", "임채원", "신현우", "권수아",
        ],
        "부서": [
            "인사", "개발", "총무", "개발", "경영", "인사",
            "개발", "총무", "경영", "개발", "인사", "총무",
        ],
        "직무": [
            "HRBP", "백엔드", "시설", "프론트엔드", "전략", "채용담당",
            "데이터", "구매", "재무", "인프라", "급여담당", "총무",
        ],
        "연차": [3, 5, 2, 1, 7, 4, 6, 2, 8, 3, 1, 4],
        "상태": [
            "재직", "재직", "재직", "수습", "재직", "재직",
            "재직", "휴직", "재직", "재직", "수습", "재직",
        ],
        "출근율": [0.98, 0.95, 0.92, 1.00, 0.97, 0.94, 0.96, 0.88, 0.99, 0.93, 1.00, 0.91],
    }
)

# 2. 사이드바 필터
st.sidebar.header("조회 조건")
department = st.sidebar.selectbox("부서", ["전체", "인사", "개발", "총무", "경영"])
status = st.sidebar.multiselect(
    "재직 상태",
    ["재직", "수습", "휴직"],
    default=["재직", "수습", "휴직"],
)
min_tenure = st.sidebar.slider("최소 연차", min_value=0, max_value=8, value=0, step=1)
name_query = st.sidebar.text_input("이름 검색", placeholder="예: 김민수")

# 3. 데이터 필터링
result = df[df["연차"] >= min_tenure].copy()
if department != "전체":
    result = result[result["부서"] == department]
if status:
    result = result[result["상태"].isin(status)]
if name_query.strip():
    result = result[result["이름"].str.contains(name_query.strip(), na=False)]

# 4. KPI
employee_count = len(result)
active_count = int((result["상태"] == "재직").sum())
leave_count = int((result["상태"] == "휴직").sum())
avg_attendance = float(result["출근율"].mean()) if len(result) else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("전체 인원", f"{employee_count}명")
k2.metric("재직", f"{active_count}명")
k3.metric("휴직", f"{leave_count}명", delta="확인 필요" if leave_count else "이상 없음")
k4.metric("평균 출근율", f"{avg_attendance * 100:.1f}%")

st.divider()

# 5. 그래프 (나란히)
graph_col1, graph_col2 = st.columns(2)

with graph_col1:
    st.subheader("부서별 인원")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    if len(result):
        dept_count = result.groupby("부서", observed=True).size().reset_index(name="인원")
        sns.barplot(data=dept_count, x="부서", y="인원", ax=ax1, color="#1a6b5c")
    ax1.set_xlabel("부서")
    ax1.set_ylabel("인원(명)")
    ax1.set_ylim(bottom=0)
    st.pyplot(fig1)
    plt.close(fig1)

with graph_col2:
    st.subheader("상태 분포")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    if len(result):
        status_count = (
            result.groupby("상태", observed=True)
            .size()
            .reindex(["재직", "수습", "휴직"], fill_value=0)
            .reset_index(name="인원")
        )
        sns.barplot(data=status_count, x="상태", y="인원", ax=ax2, color="#c45c26")
    ax2.set_xlabel("상태")
    ax2.set_ylabel("인원(명)")
    ax2.set_ylim(bottom=0)
    st.pyplot(fig2)
    plt.close(fig2)

# 6. 테이블
st.subheader("직원 목록")
st.dataframe(
    result.sort_values(["부서", "이름"]).reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
    column_config={
        "출근율": st.column_config.ProgressColumn(
            "출근율",
            min_value=0.0,
            max_value=1.0,
            format="percent",
        ),
        "연차": st.column_config.NumberColumn("연차", format="%d년"),
    },
)
