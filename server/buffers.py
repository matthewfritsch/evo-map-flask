import io


def read_all(buf: io.BytesIO | io.StringIO) -> str:
    _ = buf.seek(0)
    content = buf.read()
    _ = buf.seek(0)
    if isinstance(content, bytes):
        content = content.decode()
    return content


def write(content: str, as_bytes: bool = False) -> io.BytesIO | io.StringIO:
    if as_bytes:
        buf = io.BytesIO()
        to_write = content.encode()
        _ = buf.write(to_write)
    else:
        buf = io.StringIO()
        to_write = content
        _ = buf.write(to_write)
    _ = buf.seek(0)
    return buf

