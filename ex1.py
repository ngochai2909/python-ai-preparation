"""
====================================================================
MINI-PROJECT: AI RESUME SCREENER (LỌC CV BẤT ĐỒNG BỘ)
====================================================================
Bối cảnh: Em có 1 danh sách các đoạn text chứa nội dung CV thô.
Em cần gửi từng CV cho LLM để trích xuất thông tin và chấm điểm.
Vì có nhiều CV, quá trình này phải chạy song song (Concurrency).

YÊU CẦU:
1. Pydantic Model (Data Validation):
   - Tạo class `ResumeReview(BaseModel)`.
   - Các field:
     + candidate_name: str
     + matched_skills: list[str]
     + score: float (Điểm đánh giá, từ 0.0 đến 10.0). BẮT BUỘC dùng 
       Pydantic `Field` để validate: lớn hơn hoặc bằng 0, nhỏ hơn hoặc bằng 10.
     + is_recommended: bool

2. Hàm Mock LLM (Simulate I/O Bound):
   - Tên hàm: `call_mock_llm(cv_text: str) -> dict[str, Any]`
   - Logic: 
     + In ra màn hình: "Đang phân tích CV: {cv_text}..."
     + `await asyncio.sleep(2)` để giả lập thời gian chờ API.
     + Trả về một Dictionary CỨNG (chứa data giả) sao cho khớp 
       với cấu trúc của `ResumeReview` ở trên. (Tự chế data).

3. Hàm Xử lý Đơn (Process Single):
   - Tên hàm: `process_resume(cv_text: str) -> ResumeReview`
   - Logic: 
     + Gọi (await) hàm `call_mock_llm` ở trên để lấy data rác (dict).
     + Dùng toán tử unpacking `**` để ép cái dict đó vào class `ResumeReview`.
     + Trả về object `ResumeReview` đã được validate.

4. Hàm Chạy Song Song (Batch Process):
   - Tên hàm: `main(cv_list: list[str]) -> list[ResumeReview]`
   - Logic:
     + Nhận vào 1 mảng các chuỗi CV.
     + Dùng List Comprehension và `asyncio.gather` để chạy hàm 
       `process_resume` cho toàn bộ danh sách CV CÙNG MỘT LÚC.
     + Trả về danh sách kết quả.

5. Entry Point:
   - Khởi tạo danh sách giả: cvs = ["CV_Python_Dev", "CV_React_Dev", "CV_Data_Scientist"]
   - Dùng `asyncio.run()` để kích hoạt Event Loop chạy hàm `main(cvs)`.
   - In kết quả cuối cùng ra màn hình.
====================================================================
"""

# IMPORT THƯ VIỆN Ở ĐÂY VÀ BẮT ĐẦU CODE:
import asyncio
from typing import Any
from pydantic import BaseModel, Field

# ... (Code của em) ...


class ResumeReview(BaseModel):
    candidate_name: str
    matched_skills: list[str]
    score: float = Field(ge = 0.0, le = 10.0 )
    is_recommended: bool


async def call_mock_llm(cv_text: str) -> dict[str, Any]:
    print(f"Đang phân tích CV: {cv_text}...")
    await asyncio.sleep(2)
    return {
        "cv_name":cv_text,
        "candidate_name": "nguyen ngoc hai",
        "matched_skills": ["react", "python","js"],
        "score": 9.0,
        "is_recommended": True,
        "address":"vietnam",
        "local":"bac ninh",
        "favorite": ["sing","reading","listening to music"]
    }

async def process_resume(cv_text: str) -> ResumeReview:
    cv_data = await call_mock_llm(cv_text)
    return ResumeReview(**cv_data)

async def main(cv_list: list[str]) -> list[ResumeReview]:
    task = [process_resume(text) for text in cv_list]
    result = await asyncio.gather(
        *task
    )
    return result

cvs = ["CV_Python_Dev", "CV_React_Dev", "CV_Data_Scientist"]
result = asyncio.run(main(cvs))

print(result)
