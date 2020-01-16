# -*- coding: UTF-8 -*-

import socket
import struct

import binascii


class SockServer:

    def __init__(self):
        pass

    @classmethod
    def test(cls):
        # msg = (13, b'hellow cpp\0')
        # pak = struct.Struct('H11s')
        # buf = pak.pack(*msg)
        # print('Packed bytes :', pak.size)
        # print('Packed Value :', binascii.hexlify() binascii.hexlify(buf))
        cls.__start_server()
        # cls.__start_client()

    @classmethod
    def __start_server(cls):
        # host = '10.16.100.1'
        host = '169.254.232.79'
        port = 9001
        server = socket.socket()
        server.bind((host, port))
        server.listen(5)
        print("start server ", host + '::' + str(port))
        while True:
            client = None
            try:
                conn, addr = server.accept()
                client = conn
                print('连接地址：', addr)
                while True:
                    recv_buffer = conn.recv(1024)
                    recv_length = len(recv_buffer)
                    if recv_length > 0:
                        print('recv_buffer(%d):%s', recv_length, binascii.hexlify(recv_buffer))
                    # pak = struct.Struct('HbbbbH')
                    # buf = pak.unpack(recv_buffer)
                    # print('buf:', buf)
                    # buf = pak.pack(*msg)

                # conn.close()
            except (KeyboardInterrupt, TypeError) as e:
                print("get a error", e)

            if client is not None:
                try:
                    client.close()
                    print('client closed')
                except:
                    print('client close error')
            break
        try:
            server.close()
            print('server closed')
        except:
            print('server close error')

    @classmethod
    def __start_client(cls):
        host = '127.0.0.1'  # 获取本地主机名
        port = 9001  # 设置端口
        # 生成一个句柄
        sk = socket.socket()
        # 请求连接服务端
        sk.connect((host, port))
        print("client connect ", host + '::' + str(port))
        # 发送数据
        sk.sendall(bytes('yaoyao', 'utf8'))
        # 接受数据
        server_reply = sk.recv(1024)
        # 打印接受的数据
        print(str(server_reply, 'utf8'))
        # 关闭连接
        sk.close()
