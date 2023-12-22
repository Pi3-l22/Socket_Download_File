import socket
import sys
import zipfile  # 压缩文件
import struct  # 字符串打包解包
import json  # json序列化
from tqdm import tqdm  # 进度条

def main():
    if sys.argv[1] == '-h':
        help_message = '''
[+] 用法:
    python client.py [-h] [-H host] [-P port] [-r remote_file_path] [-l local_file_path]
    
[+] 参数说明:
    -h: 查看帮助信息
    -H: 远程服务器地址
    -P: 远程服务器端口
    -r: 远程文件路径
    -l: 本地文件路径
    '''
        print(help_message)
        return
    elif len(sys.argv) != 9:
        print('[-] 参数错误！输入-h查看帮助信息')
        return
    elif sys.argv[1] != '-H' or sys.argv[3] != '-P' or sys.argv[5] != '-r' or sys.argv[7] != '-l':
        print('[-] 参数错误！输入-h查看帮助信息')
        return

    host = sys.argv[2]
    port = sys.argv[4]
    remote_file_path = sys.argv[6]
    local_file_path = sys.argv[8]
    try:
        port = int(port)
    except Exception as e:
        print('[-] 端口号必须为整数！')
        print(e)
        return
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, port))
    except Exception as e:
        print('[-] 连接服务器失败！')
        print(e)
        return

    # 发送要下载的文件路径
    client.send(remote_file_path.encode())
    # 接收文件是否存在
    rev = client.recv(1024).decode()
    if rev == 'FILE NOT FOUND':
        print(f'[-] {remote_file_path} 文件不存在')
        client.close()
        return
    # 发送确认信息
    client.send('start_send_file'.encode())
    # 接收文件头部长度
    print('[*] 正在接收文件头部信息...')
    rev = client.recv(10)
    file_header_size = struct.unpack('i', rev)[0]
    # 发送确认信息
    client.send('header_size_ok'.encode())
    # 接收文件头部信息
    file_header_bytes = client.recv(file_header_size)
    file_header_json = file_header_bytes.decode()
    file_header = json.loads(file_header_json)
    # 发送确认信息
    client.send('header_ok'.encode())
    print(f'[+] 文件名：{file_header["file_name"]} | 文件大小：{file_header["file_size"]} B')
    # 接收文件内容
    recv_file(client, local_file_path, file_header['file_size'])


def recv_file(client_socket, local_file_path, file_size):
    try:
        with open(local_file_path, 'wb') as file:
            # 显示tqdm进度条
            for _ in tqdm(range(file_size // 1024), desc="接收中", unit="KB", unit_scale=True):
                file_data = client_socket.recv(1024)
                file.write(file_data)
    except Exception as e:
        print(f"[-] {local_file_path} 文件接收失败")
    else:
        print(f"[+] {local_file_path} 文件接收成功")


if __name__ == "__main__":
    main()