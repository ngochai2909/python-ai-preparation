import os
import chromadb
from google import genai
from dotenv import load_dotenv
from model import GEMINI_3, GEMINI_3_1, GEMINI_EMBEDING

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./my_vector_db")
collection = chroma_client.get_collection(name="movie_script")

# 1. KHỞI TẠO BỘ NHỚ
# Lưu trữ các đoạn hội thoại dưới dạng text đơn giản
chat_history = [] 

def rewrite_query(history: list, current_question: str) -> str:
    """Hàm này đóng vai trò là 'Biên tập viên'"""
    if not history:
        return current_question # Lần đầu chat thì không cần sửa
        
    history_text = "\n".join(history)


    
    prompt = f"""
    Dưới đây là lịch sử trò chuyện và một câu hỏi mới. 
    Hãy viết lại câu hỏi mới sao cho nó đầy đủ ý nghĩa nhất (thay thế các đại từ 'anh ấy', 'cô ấy', 'nó' bằng tên thật hoặc danh từ cụ thể), dựa vào ngữ cảnh của lịch sử.
    CHỈ TRẢ VỀ CÂU HỎI ĐÃ VIẾT LẠI, không giải thích gì thêm.
    
    LỊCH SỬ CHAT:
    {history_text}
    
    CÂU HỎI HIỆN TẠI: {current_question}
    """
    
    response = client.models.generate_content(
        model=GEMINI_3,
        contents=prompt
    )
    # Lấy câu hỏi đã được làm rõ
    return response.text.strip()

def chat_loop():
    print("🎬 CHATBOT KỊCH BẢN PHIM ĐÃ SẴN SÀNG! (Gõ 'exit' để thoát)")
    print("="*50)



    
    while True:
        user_input = input("\n👤 BẠN: ")
        print("="*50)
        print(f"CHAT HISTORY:{chat_history} ")
        print("="*50)
        if user_input.lower() in ['exit', 'quit']:
            print("👋 Tạm biệt!")
            break
            
        print("🔍 Đang suy nghĩ...")
        
        # --- BƯỚC 1: BIÊN TẬP LẠI CÂU HỎI ---
        standalone_question = rewrite_query(chat_history[-4:], user_input) # Chỉ lấy 4 câu gần nhất cho đỡ tốn token
        print(f"   [System Log] Câu hỏi đã viết lại: '{standalone_question}'")
        
        # --- BƯỚC 2: VECTOR SEARCH (Dùng câu hỏi đã viết lại) ---
        result = client.models.embed_content(
            model= GEMINI_EMBEDING,
            contents=standalone_question # DÙNG CÂU MỚI ĐỂ NHÚNG
        )
        question_vector = result.embeddings[0].values

        search_results = collection.query(
            query_embeddings=[question_vector],
            n_results=3
        )
        retrieved_chunks = search_results['documents'][0]
        context = "\n\n".join(retrieved_chunks)
        
        # --- BƯỚC 3: RAG PROMPT (Sinh câu trả lời) ---
        final_prompt = f"""
        Bạn là một trợ lý ảo am hiểu kịch bản phim.
        Hãy trả lời câu hỏi dựa CHỈ VÀO BỐI CẢNH dưới đây. Nếu không biết, hãy nói không biết.
        
        BỐI CẢNH TỪ KỊCH BẢN:
        {context}
        
        CÂU HỎI: {standalone_question}
        """
        
        response = client.models.generate_content(
            model=GEMINI_3,
            contents=final_prompt
        )
        
        print(f"\n🤖 BOT: {response.text}")
        
        # --- BƯỚC 4: LƯU VÀO BỘ NHỚ ---
        chat_history.append(f"User: {user_input}")
        chat_history.append(f"AI: {response.text}")




if __name__ == "__main__":
    chat_loop()