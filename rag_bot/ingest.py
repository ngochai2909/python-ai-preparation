import os
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import chromadb

load_dotenv()

# 1. Khởi tạo Gemini và ChromaDB (Database chạy ngay tại máy em)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./my_vector_db") # Lưu data vào folder này

# Tạo một "Bảng" trong database để lưu kịch bản phim
collection = chroma_client.get_or_create_collection(name="movie_script")

def ingest_pdf(file_path):
    print(f"🎬 Đang đọc kịch bản: {file_path}...")
    reader = PdfReader(file_path)
    
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()

    # 2. CHUNKING: Cắt nhỏ kịch bản (Cứ mỗi 1000 ký tự cắt 1 đoạn)
    # Trong thực tế, người ta cắt theo phân cảnh (Scene), nhưng tạm thời ta làm thế này cho đơn giản
    chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]
    print(f"📦 Đã cắt kịch bản thành {len(chunks)} đoạn nhỏ.")
    
    # 3. EMBEDDING & STORING: Biến chữ thành số và lưu vào ChromaDB
    for i, chunk in enumerate(chunks):
        # Gọi Gemini để biến đoạn văn thành Vector
        result = client.models.embed_content(
            model='gemini-embedding-2',
            contents=chunk
        )
        vector = result.embeddings[0].values
        
        # Lưu vào Database
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[vector],
            documents=[chunk]
        )
        print(f"✅ Đã số hóa đoạn {i+1}/{len(chunks)}")

    print("🚀 HOÀN TẤT! Toàn bộ kịch bản đã nằm trong Vector Database.")

if __name__ == "__main__":
    # Nhớ đổi tên này đúng với file PDF của em nhé
    ingest_pdf("nguoi_bat_tu.pdf")