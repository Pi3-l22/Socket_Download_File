import socket
import sys
import os
import zipfile  # 压缩文件
import json  # json序列化
import struct  # 字符串打包解包
import threading


def handle_client(client_socket, client_address):
    flag = False  # 是否为文件夹
    # 接收客户端发送的文件路径
    file_path = client_socket.recv(1024).decode()
    # 判断文件或者文件夹是否存在
    if os.path.exists(file_path):
        print(f"[+] 发送 {file_path} 给 {client_address}")
        # 发送文件存在的确认信息
        client_socket.send("file_exist".encode())
        # 接收客户端的确认信息
        rev = client_socket.recv(1024).decode()
        if rev != 'start_send_file':
            print(f"[-] {client_address} 取消发送 {file_path}")
            return
        # 如果是文件夹，就压缩打包成zip文件
        if os.path.isdir(file_path):
            zip_file_path = file_path + '.zip'
            zip_file = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    zip_file.write(os.path.join(root, file))
            zip_file.close()
            flag = True  # 是否为文件夹
            file_path = zip_file_path
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
        client_socket.send(header_size)
        # 接收客户端的确认信息
        rev = client_socket.recv(1024)
        if rev.decode() != 'header_size_ok':  # 如果客户端确认信息不是header_size_ok
            print(f"[-] {client_address} 取消发送 {file_path}")
            return
        # 再发送文件头部信息
        client_socket.send(file_header_bytes)
        # 接收客户端的确认信息
        rev = client_socket.recv(1024)
        if rev.decode() == 'header_ok':  # 如果客户端确认信息不是header_ok
            # 发送文件内容
            print(f'[*] 正在发送文件 {file_name} 内容...')
            send_file(client_socket, file_path, file_size)
        # 删除文件夹压缩包
        if flag:
            os.remove(file_path)
    else:
        client_socket.send("FILE NOT FOUND".encode())
        print(f"[-] {file_path} 文件不存在")


def send_file(client_socket, file_path, file_size):
    try:
        with open(file_path, 'rb') as file:
            # 显示tqdm进度条
            for _ in range(file_size // 1024):
                file_data = file.read(1024)
                client_socket.send(file_data)
    except Exception as e:
        print(f"[-] {file_path} 文件发送失败")
    else:
        print(f"[+] {file_path} 文件发送成功")



def main():
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

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)

    print(f"[*] 服务器正在监听：{host}:{port}")

    while True:
        try:
            # 接收客户端连接
            client_socket, client_address = server.accept()
            print(f"[+] 接收到客户端连接：{client_address}")
            # 多线程处理客户端请求
            # handle_client(client_socket, client_address)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        except KeyboardInterrupt:
            print("\n[-] 服务器已停止运行")
            break
    # 关闭客户端连接
    client_socket.close()

if __name__ == "__main__":
    main()