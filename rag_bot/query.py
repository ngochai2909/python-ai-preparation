import os
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

# 1. Khởi tạo Client và Kết nối lại Database
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_collection(name="movie_script")

def ask_bot(question: str):
    print(f"\n👤 BẠN HỎI: {question}")
    print("🔍 Đang lục lọi trí nhớ (Vector Search)...")

    # BƯỚC 1: Biến câu hỏi thành Vector (Phải dùng đúng model đã dùng lúc Ingest)
    result = client.models.embed_content(
        model='gemini-embedding-2',
        contents=question
    )
    print(f"kết quả embedding question: {result}")
    question_vector = result.embeddings[0].values

    # BƯỚC 2: Tìm 3 đoạn kịch bản có ngữ nghĩa gần nhất (Top K = 3)
    search_results = collection.query(
        query_embeddings=[question_vector],
        n_results=3  # Lấy 3 đoạn liên quan nhất
    )



    print("===========================================")

    print(f"SEARCH RESULT: {search_results}")
    retrieved_chunks = search_results['documents'][0]
    print("===========================================")


    print(f"RETRIEVED CHUNKS: {search_results}")

    
    # In ra để Tech Lead (là em) kiểm tra xem nó tìm có chuẩn không
    # print("\n📚 CÁC ĐOẠN TÀI LIỆU TÌM ĐƯỢC:")
    # for i, chunk in enumerate(retrieved_chunks):
    #     print(f"--- Đoạn {i+1} ---\n{chunk[:150]}...\n")

    # BƯỚC 3: Kỹ thuật "Prompt Injection" hợp pháp (Augmented Generation)
    # Gom 3 đoạn tìm được thành một đoạn văn dài
    context = "\n\n".join(retrieved_chunks)
    print("===========================================")
    print(f"CONTEXT: {context}")
    
    # Viết System Prompt gò ép AI
    prompt = f"""
    Bạn là một trợ lý ảo am hiểu sâu sắc về kịch bản phim.
    Dựa vào BỐI CẢNH (Context) được trích xuất từ kịch bản dưới đây, hãy trả lời câu hỏi của người dùng.
    
    Luật thép:
    1. CHỈ dựa vào thông tin trong BỐI CẢNH để trả lời.
    2. Nếu trong BỐI CẢNH không có thông tin, hãy nói "Trong kịch bản không đề cập đến chi tiết này", TUYỆT ĐỐI KHÔNG TỰ BỊA RA (Hallucination).

    BỐI CẢNH TỪ KỊCH BẢN:
    {context}

    CÂU HỎI CỦA NGƯỜI DÙNG: {question}
    """

    print("🤖 Đang tổng hợp câu trả lời...")
    
    # BƯỚC 4: Gọi LLM (Gemini Flash) đọc Context và trả lời
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite-preview',
        contents=prompt
    )

    print(f"\n🌟 TRẢ LỜI:\n{response.text}\n")
    print("="*50)

if __name__ == "__main__":
    # Thay câu hỏi này bằng một tình tiết CÓ THẬT trong kịch bản phim của em
    ask_bot("Nhân vật Hùng đã có siêu năng lực gì ?")
    
    # Hỏi một câu không có trong kịch bản để test luật chống "bịa chuyện"
    # ask_bot("Mật khẩu wifi của quán cà phê trong phim là gì?")