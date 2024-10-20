# 文件下载服务协议

[English](README.md) | [简体中文](README_CN.md)

本项目使用Python实现了不同网络架构下的文件下载服务协议。它包括使用单线程、多线程、select和asyncio的服务器实现,以及相应的客户端实现。

项目的详细介绍见我的博客文章：[Pi3's Notes](https://blog.pi3.fun/post/2023/12/%E4%B8%8D%E5%90%8C%E7%BD%91%E7%BB%9C%E6%9E%B6%E6%9E%84%E4%B8%8B%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD%E6%9C%8D%E5%8A%A1%E5%8D%8F%E8%AE%AE%E8%AE%BE%E8%AE%A1/)

## 特性

- 支持下载文件和目录(目录会自动压缩)
- 多种服务器架构:
  - 单线程
  - 多线程
  - 基于select
  - 基于asyncio
- 文件传输过程中显示进度条
- 可自定义服务器主机和端口
- 详细的错误处理和日志记录

## 要求

- Python 3.7+
- 所需包:
  - tqdm
  - aiofiles (用于asyncio服务器)

## 使用方法

### 服务器

选择一种服务器实现运行:

1. 单线程服务器:
   ```
   python server_singleThreading.py -P <端口>
   ```

2. 多线程服务器:
   ```
   python server_multiThreading.py -P <端口>
   ```

3. 基于select的服务器:
   ```
   python server_select.py -P <端口>
   ```

4. 基于asyncio的服务器:
   ```
   python server_asyncio.py -P <端口>
   ```

### 客户端

使用以下命令运行客户端:

```python
python client.py -H <主机> -P <端口> -r <远程文件路径> -l <本地文件路径>
```

对于基于select的客户端:
```python
python client_select.py -H <主机> -P <端口> -r <远程文件路径> -l <本地文件路径>
```

## 架构概述

1. **单线程服务器**: 按顺序处理客户端请求。
2. **多线程服务器**: 为每个客户端连接创建一个新线程。
3. **基于select的服务器**: 使用`select`模块进行非阻塞I/O操作。
4. **基于asyncio的服务器**: 利用Python的`asyncio`库进行异步I/O。

## 协议详情

1. 客户端向服务器发送请求的文件路径。
2. 服务器检查文件是否存在并发送确认。
3. 如果文件存在,服务器发送文件元数据(名称、大小、类型)。
4. 客户端确认收到元数据。
5. 服务器分块发送文件内容。
6. 客户端接收并保存文件,显示进度条。

## 错误处理

- 文件未找到
- 连接错误
- 无效的命令行参数

## 未来改进

- 添加支持恢复中断的下载
- 实现文件完整性检查(如MD5哈希验证)
- 添加加密以实现安全文件传输
- 开发客户端图形用户界面(GUI)

## 许可证

本项目是开源的,遵循[MIT许可证](LICENSE)。
