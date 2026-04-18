"""
====================================================================
THỬ THÁCH 5: BACKEND EXECUTION CHO FUNCTION CALLING
====================================================================
Bối cảnh: User chat "Thời tiết Hà Nội và Sài Gòn hôm nay thế nào?"
AI quyết định gọi hàm `get_weather` 2 lần. Nó trả về cho Backend một 
cục data chứa danh sách các Tool Calls.

YÊU CẦU CỦA TECH LEAD:
1. Pydantic Schema:
   - Tạo class `WeatherArgs(BaseModel)`.
   - Chứa 1 field: `location` (kiểu chuỗi). Dùng Field description mô tả: 
     "Tên thành phố cần xem thời tiết".

2. Hàm Python Thực Tế (Backend Tool):
   - Tạo hàm `get_weather(location: str) -> str`.
   - Logic: Chỉ cần in ra "Đang query API thời tiết cho {location}..." 
     và return "Nhiệt độ 25 độ C". (Không cần async cho đơn giản).

3. Hàm Xử lý (Agent Executor):
   - Viết hàm `execute_tool_calls(ai_response: dict) -> list[str]`.
   - Logic: 
     + Lặp qua danh sách các tool calls trong `ai_response`.
     + Lấy `arguments` (hiện đang là dict rác) ném vào class `WeatherArgs`
       để ép kiểu và validate.
     + Nếu validate thành công, lôi cái field `location` đã "sạch" đó ra 
       và truyền vào hàm `get_weather`.
     + Lưu các kết quả trả về vào một mảng và return mảng đó.
====================================================================
"""

import json
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# ĐÂY LÀ DATA GIẢ LẬP TỪ OPENAI/GEMINI TRẢ VỀ CHO BACKEND
# (KHÔNG ĐƯỢC SỬA KHỐI DATA NÀY)
mock_ai_response = {
    "tool_calls": [
        {
            "function": {
                "name": "get_weather",
                # Lưu ý: Trong thực tế AI trả arguments dạng chuỗi JSON string,
                # nhưng ở đây để đơn giản anh đã cho nó thành dict luôn:
                "arguments": {"location": "Hà Nội", "extra_crap": "abc"}
            }
        },
        {
            "function": {
                "name": "get_weather",
                "arguments": {"location": "Sài Gòn", "is_rainy": True}
            }
        }
    ],
}


# -----------------------------------

# BẮT ĐẦU CODE CỦA EM Ở DƯỚI ĐÂY:



class WeatherArgs(BaseModel):

    location:str = Field( description="Tên thành phố cần xem thời tiết")

# ----------------------
def get_weather(location: str) -> str:
    print(f"Đang query API thời tiết cho {location}...")
    result = "Nhiệt độ 25 độ C"
    return result

def execute_tool_calls(ai_response: dict) -> list[str]:
    results = []
    for tool_call in ai_response["tool_calls"]:
        raw_args = tool_call["function"]["arguments"]     
        args = WeatherArgs(**raw_args)                     
        weather = get_weather(args.location)               
        results.append(weather)
    return results

print(execute_tool_calls(mock_ai_response))