# -*- coding: utf-8 -*-
# @Time    : 2021/12/11 12:41 AM
# @Author  : Joli
# @Email   : 99755349@qq.com

import asyncio
import websockets

# 向服务器端认证，用户名密码通过才能退出循环
async def client_auth_system(websocket):
    while True:
        cred_text = input("please enter your username and password: ")
        await websocket.send(cred_text)
        response_str = await websocket.recv()
        if "congratulation" in response_str:
            return True

# 向服务器端发送认证后的消息
async def client_send_msg(websocket):
    while True:
        _text = input("please enter your context: ")
        if _text == "exit":
            print(f'you have enter "exit", goodbye')
            await websocket.close(reason="user exit")
            return False
        await websocket.send(_text)
        recv_text = await websocket.recv()
        print(f"{recv_text}")

# 客户端主逻辑
async def client_main_logic():
    # async with websockets.connect('ws://localhost:5678') as websocket:
    async with websockets.connect('ws://169.254.52.27:5678') as websocket:
        await client_auth_system(websocket)
        await client_send_msg(websocket)

def start_client():
    print("-------------------- start_client")
    asyncio.get_event_loop().run_until_complete(client_main_logic())
    print("-------------------- start_client done")

def main():
    start_client()

if __name__ == '__main__':
    main()