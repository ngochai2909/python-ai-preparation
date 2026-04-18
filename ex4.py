"""
====================================================================
MINI-PROJECT 3: SMART HOME AGENT (XỬ LÝ LỖI THIẾU DỮ LIỆU)
====================================================================
Bối cảnh: User ra lệnh: "Bật điều hòa phòng khách lên 24 độ, và khóa 
cửa chính lại giúp tôi."
AI quyết định gọi 2 hàm. Nhưng do user không nói rõ "cửa chính" là cửa 
nào (mã số bao nhiêu), con AI lười biếng đã quyết định... KHÔNG TRUYỀN 
biến `door_name` vào hàm khóa cửa luôn!

YÊU CẦU TỪ TECH LEAD:
1. Pydantic Models (Kỷ luật thép):
   - Cả 2 class vẫn BẮT BUỘC có `model_config = {"extra": "forbid"}`.
   - Class `ACArgs`: `room` (str), `temp` (int). Dùng `Field` ép `temp` 
     phải từ 16 đến 30 độ.
   - Class `DoorArgs`: `door_name` (str).

2. Fake Backend Tools (Hàm Async):
   - Hàm `async def turn_on_ac(room: str, temp: int) -> str`: 
     + `await asyncio.sleep(1)`
     + return f"Đã bật điều hòa {room} ở mức {temp} độ."
   - Hàm `async def lock_door(door_name: str) -> str`:
     + `await asyncio.sleep(1)`
     + return f"Đã khóa {door_name} an toàn."

3. Dictionary Mapping (TOOL_MAP):
   - Tự tạo lại TOOL_MAP giống bài trước để map tên hàm với function và schema.

4. Hàm Executor (Nâng cấp xử lý lỗi):
   - Viết hàm `async def execute_smart_home(ai_response: dict)`
   - Vẫn dùng try...except ValidationError như bài trước.
   - NHƯNG LẦN NÀY: Trong khối except, em không chỉ in ra e. 
     Hãy thử in ra `e.errors()` để xem Pydantic báo lỗi chi tiết đến mức nào 
     khi bị thiếu data.
   - Chạy các task hợp lệ bằng asyncio.gather.
====================================================================
"""

import asyncio
import json
from pydantic import BaseModel, Field, ValidationError

# ---------------------------------------------------------
# DATA TỪ OPENAI/GEMINI
# Con AI truyền đủ data cho điều hòa, nhưng quên truyền 'door_name' cho cửa.
mock_smarthome_payload = {
    "tool_calls": [
        {
            "function": {
                "name": "turn_on_ac",
                "arguments": '{"room": "Phòng khách", "temp": 24}'
            }
        },
        {
            "function": {
                "name": "lock_door",
                # LỖI CHÍ MẠNG Ở ĐÂY: Trống trơn, không có 'door_name'!
                "arguments": '{}' 
            }
        }
    ]
}
# ---------------------------------------------------------

# BẮT ĐẦU CODE Ở DƯỚI ĐÂY:

class ACArgs(BaseModel):
    model_config = {"extra": "forbid"}
    room: str
    temp: float = Field(ge = 16, le = 30 )

class DoorArgs(BaseModel):
    model_config = {"extra": "forbid"}
    door_name: str


async def turn_on_ac(room: str, temp: int) -> str:
    await asyncio.sleep(1)
    return f"Đã bật điều hòa {room} ở mức {temp} độ."

async def lock_door(door_name: str) -> str:
    await asyncio.sleep(1)
    return f"Đã khóa {door_name} an toàn."

TOOL_MAP = {
    "turn_on_ac": {"func": turn_on_ac, "schema": ACArgs},
    "lock_door": {"func": lock_door, "schema": DoorArgs}
}


async def execute_smart_home(ai_response: dict):
        tasks_to_run = []

        for tool_call in ai_response["tool_calls"]:
            func_name = tool_call["function"]["name"] 
            raw_args = json.loads(tool_call["function"]["arguments"])
            
            target_schema = TOOL_MAP[func_name]["schema"]
            target_func = TOOL_MAP[func_name]["func"]
            try:
                valid_args = target_schema(**raw_args) 

                tasks_to_run.append( target_func(**valid_args.model_dump()) )

            except ValidationError as e:
                print(f"❌ CẢNH BÁO: AI truyền sai data cho hàm '{func_name}'!")
                print(f"Chi tiết lỗi: {e.errors()}")
                continue 

        result = await asyncio.gather(
            *tasks_to_run
        )
        return result

response = asyncio.run(execute_smart_home(mock_smarthome_payload))
print(response)
