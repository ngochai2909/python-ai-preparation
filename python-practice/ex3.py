"""
====================================================================
MINI-PROJECT: HỆ THỐNG CSKH TỰ ĐỘNG (AGENT EXECUTOR PRO)
====================================================================
Bối cảnh: User nhắn tin phàn nàn: "Kiểm tra đơn hàng ORD-123 cho tôi, 
nếu lỗi thì hoàn tiền 50.5 đô la luôn đi!"
AI quyết định gọi 2 hàm CÙNG MỘT LÚC: `get_order_status` và `refund_order`.

YÊU CẦU TỪ TECH LEAD:
1. Pydantic Models (Kỷ luật thép):
   - Cả 2 class BẮT BUỘC phải có `model_config = {"extra": "forbid"}`.
   - Class `OrderArgs`: 1 field `order_id` (str).
   - Class `RefundArgs`: `order_id` (str), `amount` (float, phải > 0).
 
2. Fake Backend Tools (Hàm Async):
   - Hàm `async def get_order_status(order_id: str) -> str`: 
     + `await asyncio.sleep(1)`
     + return f"Đơn hàng {order_id} đang giao."
   - Hàm `async def refund_order(order_id: str, amount: float) -> str`:
     + `await asyncio.sleep(2)`
     + return f"Đã hoàn {amount}$ cho đơn {order_id}."

3. Dictionary Mapping (Bản đồ gọi hàm):
   - Tạo một dictionary tên là `TOOL_MAP` để map tên hàm (chuỗi) với 
     hàm thật (object hàm) và class Pydantic tương ứng.
   - Gợi ý: 
     TOOL_MAP = {
         "get_order_status": {"func": get_order_status, "schema": OrderArgs},
         "refund_order": {"func": refund_order, "schema": RefundArgs}
     }

4. Hàm Executor (Trái tim của hệ thống):
   - Hàm `async def execute_agent(ai_response: dict)`
   - Logic:
     + Lặp qua danh sách `tool_calls`.
     + TRÍCH XUẤT: Lấy tên hàm. Chú ý: `arguments` của AI trả về đang là 
       một CHUỖI STRING. Em PHẢI dùng `json.loads(chuoi)` để biến nó thành Dict.
     + VALIDATE: Lấy Class Schema từ `TOOL_MAP`. Bọc việc khởi tạo Pydantic 
       trong khối `try...except ValidationError as e:`. 
       Nếu lỗi (do AI ngáo đẻ thêm data), in ra thông báo lỗi và `continue` 
       (bỏ qua tool đó, không làm chết app).
     + CHUẨN BỊ: Nếu validate thành công, tạo task cho hàm thực tế và nhét 
       vào một mảng `tasks_to_run`.
     + THỰC THI CHUNG: Dùng `await asyncio.gather(*tasks_to_run)` để chạy 
       toàn bộ các tool hợp lệ một lúc.
     + In kết quả cuối cùng.
====================================================================
"""

import asyncio
import json
from pydantic import BaseModel, Field, ValidationError
from typing import Any

# ---------------------------------------------------------
# DATA TỪ OPENAI/GEMINI (CHUẨN THỰC TẾ 100%)
# Lưu ý: "arguments" là một chuỗi String (có dấu nháy kép bọc ngoài)
# Con AI đang bị ngáo, tự ý đẻ thêm field "is_urgent" ở hàm refund!
mock_payload = {
    "tool_calls": [
        {
            "function": {
                "name": "get_order_status",
                "arguments": '{"order_id": "ORD-123"}'
            }
        },
        {
            "function": {
                "name": "refund_order",
                "arguments": '{"order_id": "ORD-123", "amount": 50.5, "is_urgent": true}' 
            }
        }
    ]
}

# ---------------------------------------------------------

# BẮT ĐẦU CODE Ở DƯỚI ĐÂY:

class OrderArgs(BaseModel):
    model_config = {"extra": "forbid"}
    order_id: str


class RefundArgs(BaseModel):
    model_config = {"extra": "forbid"}
    order_id: str
    amount: float = Field(ge = 0)

async def get_order_status(order_id: str) -> str:
    await asyncio.sleep(1)
    return f"Đơn hàng {order_id} đang giao."

async def refund_order(order_id: str, amount: float) -> str:
    await asyncio.sleep(2)
    return f"Đã hoàn {amount}$ cho đơn {order_id}."


TOOL_MAP = {
    "get_order_status": {"func": get_order_status, "schema": OrderArgs},
    "refund_order": {"func": refund_order, "schema": RefundArgs}
}


async def execute_agent(ai_response: dict):
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
            print(f"Chi tiết lỗi: {e}")
            continue 

    result = await asyncio.gather(
        *tasks_to_run
    )
    return result

response = asyncio.run(execute_agent(mock_payload))
print(response)

