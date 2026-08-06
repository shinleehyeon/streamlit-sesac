import streamlit as st
st.title("인사 앱")

name = st.text_input("이름을 입력하세요")
if name:
    st.write(f"안녕하세요, {name}님! 반갑습니다.")
else:
    st.write("이름을 입력해주세요.")

if st.button("인사"):
    st.write(f"안녕하세요, {name}님! 반갑습니다.")
else:
    st.write("이름을 입력해주세요.")

st.sidebar.title("조회 조건")
dept = st.sidebar.selectbox("부서를 선택하세요", 
                     ["전체", "인사", "개발", "총무", "경영"])

st.write(f"선택한 부서: {dept}")

if st.button("재미있는 기능"):
    st.balloons()
    st.snow()
    
st.info("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.success("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.warning("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.error("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.exception(ValueError("이 기능은 실제 서비스에서는 사용할 수 없습니다."))
st.warning("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.error("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.exception(ValueError("이 기능은 실제 서비스에서는 사용할 수 없습니다."))
st.warning("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.error("이 기능은 실제 서비스에서는 사용할 수 없습니다.")
st.exception(ValueError("이 기능은 실제 서비스에서는 사용할 수 없습니다."))