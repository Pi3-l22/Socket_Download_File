# File Download Service Protocol

[English](README.md) | [简体中文](README_CN.md)

This project implements a file download service protocol using different network architectures in Python. It includes server implementations using single-threading, multi-threading, select, and asyncio, as well as corresponding client implementations.

For a detailed introduction to the project, see my blog post: [Pi3'Notes](https://blog.pi3.fun/post/2023/12/%E4%B8%8D%E5%90%8C%E7%BD%91%E7%BB%9C%E6%9E%B6%E6%9E%84%E4%B8%8B%E6%96%87%E4%BB%B6%E4%B8%8B%E8%BD%BD%E6%9C%8D%E5%8A%A1%E5%8D%8F%E8%AE%AE%E8%AE%BE%E8%AE%A1/)

## Features

- Support for downloading both files and directories (directories are automatically compressed)
- Multiple server architectures:
  - Single-threaded
  - Multi-threaded
  - Select-based
  - Asyncio-based
- Progress bar display during file transfer
- Customizable server host and port
- Detailed error handling and logging

## Requirements

- Python 3.7+
- Required packages:
  - tqdm
  - aiofiles (for asyncio server)

## Usage

### Server

Choose one of the server implementations to run:

1. Single-threaded server:
   ```python
   python server_singleThreading.py -P <port>
   ```

2. Multi-threaded server:
   ```python
   python server_multiThreading.py -P <port>
   ```

3. Select-based server:
   ```python
   python server_select.py -P <port>
   ```

4. Asyncio-based server:
   ```python
   python server_asyncio.py -P <port>
   ```

### Client

Run the client with the following command:
```python
python client.py -H <host> -P <port> -r <remote_file_path> -l <local_file_path>
```

For the select-based client:
```python
python client_select.py -H <host> -P <port> -r <remote_file_path> -l <local_file_path>
```

## Architecture Overview

1. **Single-threaded Server**: Handles client requests sequentially.
2. **Multi-threaded Server**: Creates a new thread for each client connection.
3. **Select-based Server**: Uses the `select` module for non-blocking I/O operations.
4. **Asyncio-based Server**: Utilizes Python's `asyncio` library for asynchronous I/O.

## Protocol Details

1. Client sends the requested file path to the server.
2. Server checks if the file exists and sends confirmation.
3. If the file exists, the server sends file metadata (name, size, type).
4. Client confirms receipt of metadata.
5. Server sends file content in chunks.
6. Client receives and saves the file, displaying a progress bar.

## Error Handling

- File not found
- Connection errors
- Invalid command-line arguments

## Future Improvements

- Add support for resuming interrupted downloads
- Implement file integrity checks (e.g., MD5 hash verification)
- Add encryption for secure file transfer
- Develop a graphical user interface (GUI) for the client

## License

This project is open source and available under the [MIT License](LICENSE).
