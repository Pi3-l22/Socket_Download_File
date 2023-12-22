import sys
import os
import zipfile  # 压缩文件
import json  # json序列化
import struct  # 字符串打包解包
import asyncio  # 异步IO socket
import aiofiles  # 异步文件IO


async def handle_client(reader, writer):
    # 获取客户端信息
    client_address = writer.get_extra_info('peername')
    print(f"\n[+] 接收到客户端连接：{client_address}")
    flag = False  # 是否为文件夹
    # 接收客户端发送的文件路径
    file_path = await asyncio.wait_for(reader.read(1024), None)
    file_path = file_path.decode()
    # 判断文件或者文件夹是否存在
    if os.path.exists(file_path):
        print(f"[+] 发送 {file_path} 给 {client_address}")
        # 发送文件存在的确认信息
        writer.write("file_exist".encode())
        await writer.drain()  # 清空套接字 刷新缓冲区
        # 接收客户端的确认信息
        rev = await asyncio.wait_for(reader.read(1024), None)
        if rev.decode() != 'start_send_file':
            print(f"[-] {client_address} 取消发送 {file_path}")
            return
        # 如果是文件夹，就压缩打包成zip文件
        if os.path.isdir(file_path):
            file_path = await zip_file(file_path)
        # 发送文件头部信息{文件名，文件大小，文件类型}
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_type = os.path.splitext(file_path)[1]
        file_header = {
            'file_name': file_name,
            'file_size': file_size,
            'file_type': file_type
        }
        # json序列化
        file_header_json = json.dumps(file_header)
        file_header_bytes = file_header_json.encode()
        # 将文件头部信息的长度打包成固定长度的字符串
        header_size = struct.pack('i', len(file_header_bytes))
        # 先发送文件头部信息的长度
        writer.write(header_size)
        await writer.drain()  # 清空套接字 刷新缓冲区
        # 接收客户端的确认信息
        rev = await asyncio.wait_for(reader.read(1024), None)
        if rev.decode() != 'header_size_ok':  # 如果客户端确认信息不是header_size_ok
            print(f"[-] {client_address} 取消发送 {file_path}")
            return
        # 再发送文件头部信息
        writer.write(file_header_bytes)
        await writer.drain()  # 清空套接字 刷新缓冲区
        # 接收客户端的确认信息
        rev = await asyncio.wait_for(reader.read(1024), None)
        if rev.decode() == 'header_ok':  # 如果客户端确认信息不是header_ok
            # 发送文件内容
            print(f'[*] 正在发送文件 {file_name} 内容...')
            # send_file(client_socket, file_path, file_size)
            # 异步发送文件内容
            await send_file(writer, file_path, file_size)
        # 删除文件夹压缩包
        if flag:
            os.remove(file_path)
    else:
        client_socket.send("FILE NOT FOUND".encode())
        print(f"[-] {file_path} 文件不存在")
    await writer.drain()  # 清理 刷新缓冲区
    writer.close()  # 关闭连接


async def zip_file(file_path):
    zip_file_path = file_path + '.zip'
    zip_file = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(file_path):
        for file in files:
            zip_file.write(os.path.join(root, file))
    zip_file.close()
    flag = True  # 是否为文件夹
    return zip_file_path


async def send_file(writer, file_path, file_size):
    try:
        async with aiofiles.open(file_path, 'rb') as file:
            # 显示tqdm进度条
            for _ in range(file_size // 1024):
                file_data = await file.read(1024)
                writer.write(file_data)
    except Exception as e:
        print(f"[-] {file_path} 文件发送失败\n")
    else:
        print(f"[+] {file_path} 文件发送成功\n")


async def main():
    global client_socket
    if sys.argv[1] == '-h':
        help_message = '''
[+] 用法:
    python server.py [-h] [-P port]

[+] 参数说明:
    -h: 查看帮助信息
    -P: 本地服务器监听端口
    '''
        print(help_message)
        return
    elif len(sys.argv) != 3:
        print('[-] 参数错误！输入-h查看帮助信息')
        return
    elif sys.argv[1] != '-P':
        print('[-] 参数错误！输入-h查看帮助信息')
        return
    host = '127.0.0.1'
    port = sys.argv[2]
    try:
        port = int(port)
    except Exception as e:
        print('[-] 端口号必须为整数！')
        print(e)
        return

    print(f"[*] 服务器正在监听：{host}:{port}")
    # 生成一个asyncio服务器
    server = await asyncio.start_server(handle_client, host, port)
    # 启动服务器 循环接收客户端连接
    async with server:
        await server.serve_forever()
    # 关闭客户端连接
    client_socket.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[-] 服务器已停止运行")

