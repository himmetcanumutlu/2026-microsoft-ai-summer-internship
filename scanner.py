import os
import sys

# Force UTF-8 encoding on Windows to avoid charmap errors
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import ALLOWED_EXTENSIONS, IGNORE_DIRS, CHUNK_SIZE, CHUNK_OVERLAP

def scan_and_chunk(target_directory="."):
    """
    Hedef klasörü tarar, geçerli dosyaları okur ve metin parçalarına (chunk) böler.
    """
    documents = []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len
    )

    print(f"[SCAN] Scanning started: {os.path.abspath(target_directory)}\n")

    for root, dirs, files in os.walk(target_directory):
        # Yoksayılacak klasörleri ele
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Metni parçalara böl
                    chunks = splitter.split_text(content)

                    # Her parçaya metadata (üst bilgi) ekle
                    for i, chunk in enumerate(chunks):
                        documents.append({
                            "text": chunk,
                            "metadata": {
                                "source_file": file_path,
                                "filename": file,
                                "chunk_index": i
                            }
                        })
                except Exception as e:
                    print(f"[WARN] File read error ({file_path}): {e}")

    print(f"[DONE] Scan complete! {len(documents)} chunks created.")
    return documents

if __name__ == "__main__":
    # Test çalıştırması
    chunks = scan_and_chunk(".")
    if chunks:
        print("\n--- ÖRNEK İLK PARÇA ---")
        print(f"Dosya: {chunks[0]['metadata']['filename']}")
        print(f"İçerik:\n{chunks[0]['text']}")