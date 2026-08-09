import os
import sys

# Force UTF-8 encoding on Windows to avoid charmap errors
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import streamlit as st

st.set_page_config(page_title="Yerel RAG Asistanı", page_icon="", layout="wide")

from scanner import scan_and_chunk
from database import VectorStore
from llm_client import answer_question
from config import TOP_K

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = VectorStore()
if "indexed" not in st.session_state:
    st.session_state.indexed = False


def reindex(target_dir):
    """Taramayı ve indekslemeyi baştan çalıştırır."""
    with st.spinner("Dosyalar taranıyor ve parçalara ayrılıyor..."):
        documents = scan_and_chunk(target_dir)

    if not documents:
        st.warning("Taranacak uygun dosya bulunamadı.")
        return 0

    with st.spinner(f"{len(documents)} parça ChromaDB'ye indeksleniyor..."):
        count = st.session_state.vector_store.index_documents(documents)

    st.session_state.indexed = True
    st.session_state.messages = []
    return count


# --- Sidebar ---
with st.sidebar:
    st.title(" Yerel RAG Asistanı")
    st.markdown("---")

    target = st.text_input(
        "Taranacak dizin",
        value=os.path.dirname(os.path.abspath(__file__)),
        help="Bu dizindeki .md, .py, .txt, .json dosyaları taranır.",
    )

    if st.button("Projeyi Yeniden Tara & İndeksle", type="primary", use_container_width=True):
        count = reindex(target)
        if count:
            st.success(f"{count} parça indekslendi.")
        else:
            st.error("İndeksleme başarısız.")

    st.markdown("---")

    col_stats = st.session_state.vector_store.get_collection_stats()
    if col_stats > 0:
        st.metric("İndekslenen Parça", col_stats)
        st.session_state.indexed = True

    st.markdown("---")
    st.caption("Tüm işlemler bilgisayarında çalışır — verilerin dışarı çıkmaz.")

# --- Ana Sohbet Alanı ---
st.title(" README ve Proje Dökümantasyon Asistanı")

if not st.session_state.indexed:
    st.info("Başlamak için sol menüden bir dizin seçin ve **Projeyi Yeniden Tara & İndeksle** butonuna tıklayın.")
else:
    # Geçmiş mesajları göster
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(" Kullanılan Kaynaklar (Citations)"):
                    for i, src in enumerate(msg["sources"], 1):
                        st.markdown(f"**{i}. {src['filename']}** (chunk #{src['chunk_index']}, benzerlik: {src['score']})")
                        st.caption(src["source_file"])
                        st.code(src["text"], language=None)

    # Kullanıcı girişi
    if question := st.chat_input("Proje hakkında bir soru sorun..."):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Düşünüyor..."):
                sources = st.session_state.vector_store.query(question, top_k=TOP_K)
                answer = answer_question(question, sources)

            st.markdown(answer)
            if sources:
                with st.expander(" Kullanılan Kaynaklar (Citations)"):
                    for i, src in enumerate(sources, 1):
                        st.markdown(f"**{i}. {src['filename']}** (chunk #{src['chunk_index']}, benzerlik: {src['score']})")
                        st.caption(src["source_file"])
                        st.code(src["text"], language=None)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
