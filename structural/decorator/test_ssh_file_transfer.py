"""Tests for the streaming decorators used by the SSH transfer example."""

import zlib
from collections.abc import Iterator

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .ssh_file_transfer import Encryption, compress, encrypt, read_file_stream


def test_read_file_stream_yields_file_in_chunks(tmp_path, capsys):
    """The file stream should yield all bytes without loading them at once."""
    input_path = tmp_path / "input.bin"
    input_path.write_bytes(b"a" * 8192 + b"bc")

    chunks = list(read_file_stream(input_path))

    assert chunks == [b"a" * 8192, b"bc"]
    assert capsys.readouterr().out.splitlines() == [
        "Processed: 8192 bytes",
        "Processed: 8194 bytes",
        "",
    ]


def test_compress_decorator_produces_valid_zlib_stream():
    """The compression decorator should preserve the complete source data."""

    @compress
    def source() -> Iterator[bytes]:
        yield b"repeated data " * 10
        yield b"final chunk"

    compressed = b"".join(source())

    assert zlib.decompress(compressed) == (
        b"repeated data " * 10 + b"final chunk"
    )


def test_encrypt_decorator_encrypts_each_chunk():
    """The encryption decorator should frame each chunk independently."""
    encryption = Encryption()
    plaintext_chunks = [b"first chunk", b"second chunk"]

    @encrypt(encryption)
    def source() -> Iterator[bytes]:
        yield from plaintext_chunks

    decrypted_chunks = []
    cipher = AESGCM(encryption.key)
    for framed_chunk in source():
        nonce = framed_chunk[: Encryption.NONCE_SIZE]
        size_start = Encryption.NONCE_SIZE
        size_end = size_start + 4
        ciphertext_size = int.from_bytes(
            framed_chunk[size_start:size_end], "big"
        )
        ciphertext = framed_chunk[size_end:]

        assert len(ciphertext) == ciphertext_size
        decrypted_chunks.append(cipher.decrypt(nonce, ciphertext, None))

    assert decrypted_chunks == plaintext_chunks
