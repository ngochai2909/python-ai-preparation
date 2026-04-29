import chromadb
import json

# 1. Kết nối lại vào Database
chroma_client = chromadb.PersistentClient(path="./my_vector_db")

# 2. Lấy ra cái bảng (collection) chứa kịch bản
collection = chroma_client.get_collection(name="movie_script")

# Kiểm tra tổng số dòng data (COUNT trong SQL)
total_chunks = collection.count()
print(f"📊 Tổng số chunk đang có trong DB: {total_chunks}\n")

# 3. Dùng hàm peek() để xem thử 2 dòng đầu tiên (giống LIMIT 2)
data = collection.peek(limit = 2)

# Mổ xẻ dữ liệu trả về
print("=== 🆔 DANH SÁCH ID ===")
print(data['ids'])  # Ví dụ: ['chunk_0', 'chunk_1']

print("\n=== 📝 NỘI DUNG TEXT (DOCUMENTS) ===")
for doc in data['documents']:
    print(f"- {doc[:100]}...") # In 100 chữ đầu của mỗi đoạn cho đỡ dài

print("\n=== 🔢 VECTOR (EMBEDDINGS) ===")
# Lấy vector đầu tiên ra xem
first_vector = data['embeddings'][0]
print(f"Số lượng con số (số chiều) của 1 chunk: {len(first_vector)}")
print(f"Hiển thị thử 5 con số đầu tiên: {first_vector[:5]}...")