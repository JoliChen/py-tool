# -*- coding: utf-8 -*-
# @Time    : 2021/12/11 12:10 AM
# @Author  : Joli
# @Email   : 99755349@qq.com

import asyncio
import websockets

# 检测客户端权限，用户名密码通过才能退出循环
async def server_check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)

# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
async def server_recv_msg(websocket):
    while True:
        recv_text = await websocket.recv()
        response_text = f"your submit context: {recv_text}"
        await websocket.send(response_text)

# 服务器端主逻辑
# websocket和path是该函数被回调时自动传过来的，不需要自己传
async def server_main_logic(websocket, path):
    print("-----", path)
    await server_check_permit(websocket)
    await server_recv_msg(websocket)

def start_server():
    print("-------------------- start_server")
    # 把ip换成自己本地的ip
    # ws_server = websockets.serve(server_main_logic, 'localhost', 5678)
    ws_server = websockets.serve(server_main_logic, '169.254.52.27', 5678)
    # 如果要给被回调的main_logic传递自定义参数，可使用以下形式
    # 一、修改回调形式
    # import functools
    # ws_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), '10.10.6.91', 5678)
    # 修改被回调函数定义，增加相应参数
    # async def main_logic(websocket, path, other_param)

    asyncio.get_event_loop().run_until_complete(ws_server)
    asyncio.get_event_loop().run_forever()
    print("-------------------- start_server done")

def main():
    start_server()

if __name__ == '__main__':
    main()