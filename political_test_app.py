
import streamlit as st, pandas as pd, altair as alt

questions = pd.read_excel("politics_test_questions.xlsx")

BASE = 30
x_score = y_score = BASE

# 축별 ‘진보’ 문항 수 = 기본점수
PROG_X = len(questions[(questions.axis=="economic") & (questions.bloc=="progressive")])
PROG_Y = len(questions[(questions.axis=="social")   & (questions.bloc=="progressive")])

st.title("대한민국 정치성향 테스트")
st.caption("각 문항을 펼쳐 설명 확인 후 **예 / 아니요 / 상관없음** 을 선택하세요.")

answer_map = {"예":1, "아니요":-1, "상관없음":0}
responses = {}
with st.form("quiz"):
    for _, row in questions.iterrows():
        key = f"q{row.id}"
        with st.expander(row.statement):
            pros = str(row.get("pros", "")).strip()
            cons = str(row.get("cons", "")).strip()

            if pros or cons:
                c1, c2 = st.columns(2)
                if pros:
                    with c1:
                        st.markdown("#### ✅ 기대효과")
                        st.markdown(pros)
                if cons:
                    with c2:
                        st.markdown("#### ⚠️ 우려")
                        st.markdown(cons)

            responses[key] = st.radio("선택", ("예","아니요","상관없음"),
                                      key=key, horizontal=True)
    submitted = st.form_submit_button("결과 보기")

if submitted:
    for _, row in questions.iterrows():
        ans = answer_map[responses[f"q{row.id}"]]
        if ans == 0:
            continue
        aligns_conservative = ((ans==1 and row.bloc=="conservative") or
                               (ans==-1 and row.bloc=="progressive"))
        delta = 1 if aligns_conservative else -1
        if row.axis == "economic":
            x_score += delta
        else:
            y_score += delta

    st.subheader("📊 내 정치 좌표")
    st.write(f"경제 축 (0=좌파 · 60=우파) : **{x_score} / 60**")
    st.write(f"사회 축 (0=진보 · 60=보수) : **{y_score} / 60**")

    # ── Altair 시각화 ───────────────────────────
    domain = [0, 60]

    # ① 사용자 점
    pt = alt.Chart(pd.DataFrame({'x':[x_score],'y':[y_score]})).mark_point(
            size=130, filled=True, color='red'
    ).encode(
            x=alt.X('x:Q', scale=alt.Scale(domain=domain),
                    axis=alt.Axis(title='경제 축 (0 = 좌파 ▸ 60 = 우파)')),
            y=alt.Y('y:Q', scale=alt.Scale(domain=domain),
                    axis=alt.Axis(title='사회 축 (0 = 진보 ▸ 60 = 보수)'))
    )

    # ② 중앙 분할선 2개
    vline = alt.Chart(pd.DataFrame({'x':[30]})).mark_rule(
                strokeDash=[4,4], color='gray'
    ).encode(x='x:Q')
    hline = alt.Chart(pd.DataFrame({'y':[30]})).mark_rule(
                strokeDash=[4,4], color='gray'
    ).encode(y='y:Q')

    chart = alt.layer(pt, vline, hline).resolve_scale(x='shared', y='shared')                                       .properties(width=500, height=500)

    st.altair_chart(chart, use_container_width=False)

    st.info("왼쪽 아래 ⇒ 경제·사회 모두 진보 / 오른쪽 위 ⇒ 경제·사회 모두 보수")
