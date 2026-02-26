import streamlit as st

from emacs_assistant import ask_emacs

st.set_page_config(page_title="Emacs Learning Assistant", page_icon="E")
st.title("Emacs Learning Assistant")
st.caption("Plain-language help for learning Emacs features and workflows")

skill_level = st.selectbox(
    "Your current comfort level",
    ["beginner", "intermediate", "advanced"],
    index=0,
)

user_query = st.text_input(
    "Ask an Emacs question",
    placeholder="Example: How do I open files and switch buffers?",
)

if st.button("Get Answer", type="primary"):
    if not user_query.strip():
        st.warning("Enter a question first.")
    else:
        with st.spinner("Generating answer..."):
            result = ask_emacs(user_query, skill_level=skill_level)

        st.markdown("### Answer")
        st.write(result["answer"])

        st.caption(f"Provider: {result.get('provider', 'unknown')} | Model: {result.get('model', 'unknown')}")

        if result["sources"]:
            st.markdown("### Sources")
            for src in result["sources"]:
                st.code(src)
