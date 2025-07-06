import io


def read_all(buf: io.BytesIO) -> str:
    _ = buf.seek(0)
    content = buf.read()
    _ = buf.seek(0)
    return content.decode()


def write(content: str) -> io.StringIO:
    buf = io.StringIO()
    _ = buf.write(content)
    _ = buf.seek(0)
    return buf
