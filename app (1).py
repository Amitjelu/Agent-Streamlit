import streamlit as st

st.title('🧠The Memory Test')

col1, col2 = st.columns(2)

with col1:
    st.subheader('Normal Variable')

    normal_counter = 0

    if st.button("Click Me (Normal)"):
        normal_counter = normal_counter + 1

    st.write(f'Normal Counter: {normal_counter}')

with col2:
    st.subheader('Session State')

    if 'counter' not in st.session_state: # Will only work when we first time open the website
        st.session_state.counter = 0

    if st.button('Click Me(Remember)'):
        st.session_state.counter = st.session_state.counter + 1

    st.write(f'Memory Counter: {st.session_state.counter}')
