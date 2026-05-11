import streamlit as st
import requests

API_URL = "http://app:5000"

st.set_page_config(page_title="Medical RAG Assistant", layout="wide")
st.title("Medical Drug Information Assistant")
st.markdown("Upload a drug leaflet PDF and ask questions about it.")

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.header("Project Settings")
project_id = st.sidebar.text_input("Project ID", value="medproject")
language = st.sidebar.selectbox("Language / اللغة", ["en", "ar"])
chunk_size = st.sidebar.slider("Chunk Size", 100, 1000, 300)
overlap = st.sidebar.slider("Overlap", 0, 200, 50)
top_k = st.sidebar.slider("Top K Results", 1, 10, 5)
do_reset = st.sidebar.checkbox("Reset existing data before processing", value=True)

# ── Step 1: Upload ────────────────────────────────────────────────────────────
st.header("Upload a Document")
uploaded_file = st.file_uploader("Choose a PDF or TXT file", type=["pdf", "txt"])

if uploaded_file and st.button("Upload"):
    with st.spinner("Uploading..."):
        response = requests.post(
            f"{API_URL}/api/data/upload/{project_id}",
            files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        )
    if response.status_code == 200:
        st.success(f"Uploaded successfully: {uploaded_file.name}")
        st.session_state["file_name"] = uploaded_file.name
    else:
        st.error(f"Upload failed: {response.text}")

# ── Step 2: Process ───────────────────────────────────────────────────────────
st.header("Process Document into Chunks")

if st.button("Process Document"):
    file_name = st.session_state.get("file_name")
    if not file_name:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("Processing..."):
            response = requests.post(
                f"{API_URL}/api/data/process/{project_id}",
                json={
                    "file_name": file_name,
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                    "do_reset": 1 if do_reset else 0
                }
            )
        if response.status_code == 200:
            data = response.json()
            st.success(f"Created {data['chunks_created']} chunks successfully.")
        else:
            st.error(f"Processing failed: {response.text}")

# ── Step 3: Push to Index ─────────────────────────────────────────────────────
st.header("Push to Vector Index")

if st.button("Push to Index"):
    with st.spinner("Embedding and indexing chunks..."):
        response = requests.post(
            f"{API_URL}/api/nlp/index/push/{project_id}",
            json={"do_reset": 1 if do_reset else 0}
        )
    if response.status_code == 200:
        st.success(response.json()["message"])
    else:
        st.error(f"Push failed: {response.text}")

# ── Step 4: Ask a Question ────────────────────────────────────────────────────
st.header("Ask a Question")

query = st.text_input("Your question", placeholder="What are the side effects of this drug?")

col1, col2 = st.columns(2)

with col1:
    if st.button("Search Chunks"):
        if not query:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching..."):
                response = requests.post(
                    f"{API_URL}/api/nlp/index/search/{project_id}",
                    json={"text": query, "top_k": top_k, "language": language}
                )
            if response.status_code == 200:
                data = response.json()
                results = data["results"]
                st.subheader("Retrieved Chunks")
                search_query = data.get("search_query")
                if search_query and search_query != query:
                    st.caption(f"Search query: {search_query}")
                for i, r in enumerate(results):
                    with st.expander(f"Chunk {i+1} — Score: {r['score']:.4f}"):
                        st.write(r["text"])
            else:
                st.error("Search failed.")

with col2:
    if st.button("Get RAG Answer"):
        if not query:
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating answer..."):
                response = requests.post(
                    f"{API_URL}/api/nlp/index/answer/{project_id}",
                    json={"text": query, "top_k": top_k, "language": language}
                )
            if response.status_code == 200:
                data = response.json()
                st.subheader("Answer")
                st.markdown(data["answer"])
                with st.expander("View Full Prompt"):
                    st.text(data["full_prompt"])
            else:
                st.error("Answer generation failed.")
