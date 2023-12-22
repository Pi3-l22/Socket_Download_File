import socket
import sys
import os
import selectors  # selectors模块单线程异步轮询


def send_file(client_socket, file_path, file_size):
    try:
        with open(file_path, 'rb') as file:
            # 显示tqdm进度条
            for _ in range(file_size // 1024):
                file_data = file.read(1024)
                try:
                    client_socket.send(file_data)
                except BlockingIOError:
                    pass
    except Exception as e:
        print(f"[-] {file_path} 文件发送失败\n")
        print(e)
    else:
        print(f"[+] {file_path} 文件发送成功\n")


def accept(sock, mask):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)  # 设定非阻塞
    sel.register(conn, selectors.EVENT_READ, read)  # 新连接注册read回调函数


def read(conn, mask):
    global rev
    file_path = conn.recv(1024).decode()
    if file_path:
        # 发送文件
        if os.path.exists(file_path):
            print(f"[+] 发送 {file_path}")
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            # 发送文件大小
            conn.send(str(file_size).encode())
            # 接收客户端的确认信息
            try:
                rev = conn.recv(1024).decode()
                if rev:
                    if rev != 'file_size_ok':
                        print(f"[-] {conn} 取消发送 {file_path}")
                        return
            except BlockingIOError:
                pass
            send_file(conn, file_path, file_size)
        else:
            try:
                conn.send('FILE NOT FOUND'.encode())
            except BlockingIOError:
                pass
    else:
        print('closing', conn)
        sel.unregister(conn)
        conn.close()


# selectors模块默认会用epoll，如果你的系统中没有epoll(比如windows)则会自动使用select
sel = selectors.DefaultSelector()  # 生成一个select对象

if sys.argv[1] == '-h':
    help_message = '''
[+] 用法:
python server.py [-h] [-P port]

[+] 参数说明:
-h: 查看帮助信息
-P: 本地服务器监听端口
'''
    print(help_message)
    sys.exit()
elif len(sys.argv) != 3:
    print('[-] 参数错误！输入-h查看帮助信息')
    sys.exit()
elif sys.argv[1] != '-P':
    print('[-] 参数错误！输入-h查看帮助信息')
    sys.exit()
host = '127.0.0.1'
port = sys.argv[2]
try:
    port = int(port)
except Exception as e:
    print('[-] 端口号必须为整数！')
    print(e)
    sys.exit()

sock = socket.socket()
sock.bind((host, port))
sock.listen()
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)  # 把刚生成的sock连接对象注册到select连接列表中，并交给accept函数处理
print(f"[*] 服务器正在监听：{host}:{port}")
while True:
    events = sel.select()  # 默认是阻塞，有活动连接就返回活动的连接列表
    # 这里看起来是select，其实有可能会使用epoll，如果你的系统支持epoll，那么默认就是epoll
    for key, mask in events:
        callback = key.data  # 去调accept函数
        callback(key.fileobj, mask)  # key.fileobj就是readable中的一个socket连接对象
