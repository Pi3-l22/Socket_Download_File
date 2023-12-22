import socket
import sys
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
    # 接收文件内容
    print('[*] 正在接收文件内容...')
    # 发送要下载的文件路径
    client.send(remote_file_path.encode())
    try:
        file_size = int(client.recv(1024).decode())
    except Exception as e:
        print('[-] 文件不存在！')
        print(e)
        return
    # 发送确认信息
    client.send('start_send_file'.encode())
    with open(local_file_path, 'wb') as file:
        for _ in tqdm(range(file_size // 1024)):
            file_data = client.recv(1024)
            file.write(file_data)


if __name__ == "__main__":
    main()
