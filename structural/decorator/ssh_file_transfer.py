"""Stream a compressed and encrypted file to another computer over SSH."""

import functools
import os
import subprocess
import zlib
from collections.abc import Iterator
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class Encryption:
    """Provide authenticated encryption using AES-GCM."""

    NONCE_SIZE = 12

    def __init__(self, key_length: int = 256) -> None:
        """Create a random key and initialize the AES-GCM cipher."""
        self._key = AESGCM.generate_key(bit_length=key_length)
        self._cipher = AESGCM(self._key)

    @property
    def key(self) -> bytes:
        """Return the encryption key."""
        return self._key

    def encrypt(self, chunk: bytes) -> bytes:
        """Encrypt and frame the provided bytes."""
        nonce = os.urandom(self.NONCE_SIZE)
        ciphertext = self._cipher.encrypt(nonce, chunk, None)
        return nonce + len(ciphertext).to_bytes(4, "big") + ciphertext


def encrypt(encryption: Encryption):
    """Decorate a byte stream factory to encrypt every yielded chunk."""

    def decorator_encrypt(stream_func):
        @functools.wraps(stream_func)
        def wrapper_encrypt(*args, **kwargs) -> Iterator[bytes]:
            for chunk in stream_func(*args, **kwargs):
                yield encryption.encrypt(chunk)

        return wrapper_encrypt

    return decorator_encrypt


def compress(stream_func):
    """Decorate a byte stream factory with incremental zlib compression."""

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
    """Decorate a byte stream factory to report its cumulative byte count."""

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
    """Yield a file's contents in eight-kilobyte chunks."""
    with file_path.open("rb") as file:
        while chunk := file.read(1024 * 8):
            yield chunk


def send_file_to_local_pc(
    *,
    username: str,
    ip_address: str,
    input_path: Path,
    output_filename: str,
):
    """Send a compressed and encrypted file to another local-network PC."""
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
                    (
                        "$outputStream = "
                        f"[IO.File]::Create('C:\\Users\\{username}\\"
                        f"{output_filename}')"
                    ),
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
