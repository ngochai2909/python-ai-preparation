"""
====================================================================
MINI-PROJECT 4: ĐƯA AGENT LÊN WEB API (HỢP THỂ)
====================================================================
Bối cảnh: Em cần làm một API để Frontend gọi vào. Khi Frontend gửi 
tin nhắn, API sẽ (giả vờ) nhờ AI phân tích, sau đó chạy các Tool 
tương ứng (Điều hòa, Khóa cửa) và trả kết quả về cho Frontend.

YÊU CẦU:
1. Bê toàn bộ Class Pydantic (ACArgs, DoorArgs) và các hàm Tools 
   (turn_on_ac, lock_door, TOOL_MAP) từ bài Smart Home trước nhét vào đây.
   
2. Chỉnh sửa hàm `execute_smart_home`:
   - Ở bài trước, khi bắt được ValidationError, em chỉ `print` ra màn hình.
   - BÂY GIỜ: Em phải gom các lỗi đó vào một mảng `errors = []`.
   - Hàm phải return về cả 2 thứ: `return results, errors`.
   (Để API còn biết đường báo lại cho Frontend là AI bị ngáo chỗ nào).

3. Endpoint POST `/api/v1/command`:
   - Nhận vào `CommandRequest` (chứa `user_message`).
   - Gọi hàm `await execute_smart_home(mock_smarthome_payload)`. 
     (Giả vờ như payload này là do AI sinh ra từ câu user_message).
   - Trả về JSON chứa cả kết quả chạy thành công và danh sách lỗi.
====================================================================
"""

import asyncio
import json
from fastapi import FastAPI
from pydantic import BaseModel, Field, ValidationError

app = FastAPI()

# --- 1. COPY Pydantic Models & Tools từ bài trước paste vào đây ---
# class ACArgs...
# class DoorArgs...
# async def turn_on_ac...
# async def lock_door...
# TOOL_MAP = {...}

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

# ---------------------------------------------------------
# DATA MOCK (AI quên truyền door_name)
mock_smarthome_payload = {
    "tool_calls": [
        {"function": {"name": "turn_on_ac", "arguments": '{"room": "Phòng khách", "temp": 24}'}},
        {"function": {"name": "lock_door", "arguments": '{}'}} 
    ]
}
# ---------------------------------------------------------

# --- 2. HÀM EXECUTOR (Nâng cấp) ---
async def execute_smart_home(ai_response: dict):
    tasks_to_run = []
    errors = [] # MỚI: Mảng chứa lỗi để báo cho Frontend
    
    for tool_call in ai_response["tool_calls"]:
        func_name = tool_call["function"]["name"] 
        raw_args = json.loads(tool_call["function"]["arguments"])
        
        target_schema = TOOL_MAP[func_name]["schema"]
        target_func = TOOL_MAP[func_name]["func"]
        
        try:
            valid_args = target_schema(**raw_args) 
            tasks_to_run.append(target_func(**valid_args.model_dump()))
        except ValidationError as e:
            # MỚI: Thay vì print, hãy thêm thông báo lỗi vào mảng errors
            # Gợi ý: errors.append(f"Lỗi ở hàm {func_name}: Thiếu data!")
            ...
            continue 

    results = await asyncio.gather(*tasks_to_run)
    
    # MỚI: Trả về cả 2 mảng
    return results, errors

# --- 3. ENDPOINT API CỦA FASTAPI ---
class CommandRequest(BaseModel):
    user_message: str

@app.post("/api/v1/command")
async def run_agent_command(payload: CommandRequest):
    print(f"Nhận được lệnh từ User: {payload.user_message}")
    
    # Chạy Agent (dùng await vì hàm execute_smart_home là async)
    success_results, ai_errors = await execute_smart_home(mock_smarthome_payload)
    
    # Trả về kết quả cho Frontend
    return {
        "status": "completed",
        "actions_taken": success_results,
        "warnings": ai_errors
    }