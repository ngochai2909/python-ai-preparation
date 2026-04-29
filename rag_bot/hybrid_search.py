import os
import chromadb
from google import genai
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from model import GEMINI_3, GEMINI_3_1, GEMINI_EMBEDING

load_dotenv()

# 1. Khởi tạo
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_collection(name="movie_script")

# Lấy TOÀN BỘ dữ liệu từ ChromaDB ra để nạp vào BM25 (Trong thực tế người ta dùng ElasticSearch, nhưng học thì dùng cách này cho lẹ)
all_data = collection.get()
all_chunks = all_data['documents']
all_ids = all_data['ids']

# 2. CHUẨN BỊ BM25 (Băm nhỏ text thành các từ rời rạc)
tokenized_corpus = [doc.lower().split(" ") for doc in all_chunks]
bm25 = BM25Okapi(tokenized_corpus)

def hybrid_search(query: str, top_k: int = 3):
    print(f"\n🔍 TÌM KIẾM LAI CHO CÂU HỎI: '{query}'")
    
    # === LUỒNG 1: TÌM KIẾM TỪ KHÓA (BM25) ===
    tokenized_query = query.lower().split(" ")

    print("="*50)
    print(f"tokenize query: {tokenized_query}")

    # Lấy điểm số từ khóa cho từng chunk
    bm25_scores = bm25.get_scores(tokenized_query) 
    print("="*50)
    print(f"bm25_scoresy: {bm25_scores}")
    # Xếp hạng và lấy ra top K ID
    top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
    bm25_results = [all_ids[i] for i in top_bm25_indices]

    print("="*50)
    print(f"bm25_results: {bm25_results}")
    
    # === LUỒNG 2: TÌM KIẾM NGỮ NGHĨA (VECTOR CHROMA) ===
    result = client.models.embed_content(
        model=GEMINI_EMBEDING,
        contents=query
    )
    print("="*50)
    print(f"result: {result}")
    
    vector_results = collection.query(
        query_embeddings=[result.embeddings[0].values],
        n_results=top_k
    )
    print("="*50)
    print(f"vector_results: {vector_results}")

    chroma_results = vector_results['ids'][0]

    print(f"   [BM25] Tìm thấy các ID: {bm25_results}")
    print(f"   [Vector] Tìm thấy các ID: {chroma_results}")

    # === LUỒNG 3: TRỘN KẾT QUẢ (RRF - Reciprocal Rank Fusion) ===
    # Công thức RRF đơn giản: Điểm RRF = 1 / (Hạng_BM25 + 60) + 1 / (Hạng_Vector + 60)
    rrf_scores = {}
    
    for rank, doc_id in enumerate(bm25_results):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (rank + 1 + 60)
        
    for rank, doc_id in enumerate(chroma_results):
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1.0 / (rank + 1 + 60)

    # Sắp xếp lại theo điểm RRF giảm dần
    final_ranked_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)[:top_k]
    
    print("\n🏆 KẾT QUẢ CUỐI CÙNG SAU KHI TRỘN (RRF):")
    for doc_id in final_ranked_ids:
        # Lấy nội dung text dựa vào ID
        idx = all_ids.index(doc_id)
        print(f"   👉 ID: {doc_id} | Điểm RRF: {rrf_scores[doc_id]:.5f}")
        print(f"      Trích xuất: {all_chunks[idx][:100]}...\n")



if __name__ == "__main__":
    # Test tìm kiếm bằng một tên riêng hoặc 1 từ khóa chính xác có trong kịch bản của em
    hybrid_search("Hùng")