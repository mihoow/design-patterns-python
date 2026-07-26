"""main."""

import functools
import os
import subprocess
import zlib
from collections.abc import Iterator
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Encryption:
    """Represents encryption/decryption algorithm."""

    NONCE_SIZE = 12

    def __init__(self, key_length: int = 256) -> None:
        """Create the algorithm key and cipher."""
        self._key = AESGCM.generate_key(bit_length=key_length)
        self._cipher = AESGCM(self._key)

    @property
    def key(self) -> bytes:
        """Return algorithm key."""
        return self._key

    def encrypt(self, chunk: bytes) -> bytes:
        """Encrypt provided chunk."""
        nonce = os.urandom(self.NONCE_SIZE)
        ciphertext = self._cipher.encrypt(nonce, chunk, None)

        return nonce + len(ciphertext).to_bytes(4, "big") + ciphertext


def encrypt(encryption: Encryption):
    """Encrypt each chunk of a stream using provided encryption mechanism."""

    def decorator_encrypt(stream_func):
        @functools.wraps(stream_func)
        def wrapper_encrypt(*args, **kwargs) -> Iterator[bytes]:
            for chunk in stream_func(*args, **kwargs):
                yield encryption.encrypt(chunk)

        return wrapper_encrypt

    return decorator_encrypt


def compress(stream_func):
    """Compress each chunk of a stream."""

    @functools.wraps(stream_func)
    def wrapper_compress(*args, **kwargs) -> Iterator[bytes]:
        compressor = zlib.compressobj(level=6)

        for chunk in stream_func(*args, **kwargs):
            compressed = compressor.compress(chunk)
            if compressed:
                yield compressed
        final_data = compressor.flush()
        if final_data:
            yield final_data

    return wrapper_compress


def log_progress(stream_func):
    """Log streaming progress."""

    @functools.wraps(stream_func)
    def wrapper_progress(*args, **kwargs) -> Iterator[bytes]:
        total_size = 0

        for chunk in stream_func(*args, **kwargs):
            total_size += len(chunk)
            print(f"Processed: {total_size} bytes")
            yield chunk

        print()

    return wrapper_progress


@log_progress
def read_file_stream(file_path: Path):
    """Create file chunks iterator."""
    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 8):
            yield chunk


def send_file_to_local_pc(
    *, username: str, ip_address: str, input_path: Path, output_filename: str
):
    """Send a file to a local computer."""
    process = subprocess.Popen(
        [
            "ssh",
            f"{username}@{ip_address}",
            "powershell",
            "-NoProfile",
            "-Command",
            "; ".join(
                [
                    "$inputStream = [Console]::OpenStandardInput()",
                    f"$outputStream = [IO.File]::Create('C:\\Users\\{username}\\{output_filename}')",  # noqa: E501
                    "$inputStream.CopyTo($outputStream)",
                    "$outputStream.Dispose()",
                ]
            ),
        ],
        stdin=subprocess.PIPE,
    )

    @encrypt(Encryption(key_length=256))
    @compress
    def read_input_file():
        return read_file_stream(input_path)

    for chunk in read_input_file():
        process.stdin.write(chunk)

    process.stdin.close()
    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(f"Transfer ended with code: {return_code}")


if __name__ == "__main__":
    send_file_to_local_pc(
        username="m98wi",
        ip_address="192.168.1.11",
        input_path=Path(__file__).resolve().parent / "input.txt",
        output_filename="ssh_output.bin",
    )
