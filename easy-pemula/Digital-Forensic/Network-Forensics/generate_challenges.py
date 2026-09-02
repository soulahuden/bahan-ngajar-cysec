#!/usr/bin/env python3
"""Generate two deterministic, beginner-friendly, 30-packet CTF captures."""

from __future__ import annotations

import ipaddress
import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FLAG = b"FLAG{basic_pc4p_analysis}"


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def mac(value: str) -> bytes:
    return bytes.fromhex(value.replace(":", ""))


def ipv4(value: str) -> bytes:
    return ipaddress.IPv4Address(value).packed


def ethernet(payload: bytes, src: str, dst: str) -> bytes:
    return mac(dst) + mac(src) + struct.pack("!H", 0x0800) + payload


def ip_packet(payload: bytes, src: str, dst: str, protocol: int, ident: int) -> bytes:
    src_raw = ipv4(src)
    dst_raw = ipv4(dst)
    header = struct.pack(
        "!BBHHHBBH4s4s",
        0x45,
        0,
        20 + len(payload),
        ident,
        0x4000,
        64,
        protocol,
        0,
        src_raw,
        dst_raw,
    )
    header = header[:10] + struct.pack("!H", checksum(header)) + header[12:]
    return header + payload


def icmp_echo(data: bytes, echo_id: int, sequence: int, reply: bool) -> bytes:
    message_type = 0 if reply else 8
    packet = struct.pack("!BBHHH", message_type, 0, 0, echo_id, sequence) + data
    return packet[:2] + struct.pack("!H", checksum(packet)) + packet[4:]


def tcp_segment(
    payload: bytes,
    src_ip: str,
    dst_ip: str,
    src_port: int,
    dst_port: int,
    seq: int,
    ack: int,
    flags: int,
) -> bytes:
    offset_and_flags = (5 << 12) | flags
    header = struct.pack(
        "!HHIIHHHH",
        src_port,
        dst_port,
        seq,
        ack,
        offset_and_flags,
        65535,
        0,
        0,
    )
    segment = header + payload
    pseudo = (
        ipv4(src_ip)
        + ipv4(dst_ip)
        + struct.pack("!BBH", 0, 6, len(segment))
        + segment
    )
    return header[:16] + struct.pack("!H", checksum(pseudo)) + header[18:] + payload


def write_pcap(path: Path, frames: list[bytes], base_time: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output:
        output.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 262144, 1))
        for index, frame in enumerate(frames):
            timestamp = base_time + index // 100
            microseconds = (index % 100) * 10_000
            output.write(struct.pack("<IIII", timestamp, microseconds, len(frame), len(frame)))
            output.write(frame)


def build_network1() -> list[bytes]:
    client_ip = "192.168.10.15"
    server_ip = "192.168.10.1"
    client_mac = "02:00:00:00:10:15"
    server_mac = "02:00:00:00:10:01"
    parts = {
        5: b"part1=FLAG{basic_",
        10: b"part2=pc4p_",
        15: b"part3=analysis}",
    }
    frames: list[bytes] = []

    for sequence in range(1, 16):
        request_data = f"health-check sequence={sequence:02d}".encode()
        reply_data = parts.get(sequence, f"status=ok sequence={sequence:02d}".encode())

        request = icmp_echo(request_data, 0x1337, sequence, reply=False)
        request_ip = ip_packet(request, client_ip, server_ip, 1, 1000 + sequence * 2)
        frames.append(ethernet(request_ip, client_mac, server_mac))

        reply = icmp_echo(reply_data, 0x1337, sequence, reply=True)
        reply_ip = ip_packet(reply, server_ip, client_ip, 1, 1001 + sequence * 2)
        frames.append(ethernet(reply_ip, server_mac, client_mac))

    return frames


def png_with_flag(source: Path) -> bytes:
    png = source.read_bytes()
    signature = b"\x89PNG\r\n\x1a\n"
    if not png.startswith(signature):
        raise ValueError(f"{source} is not a PNG file")

    iend_offset = png.rfind(b"\x00\x00\x00\x00IEND")
    if iend_offset < 8:
        raise ValueError(f"{source} has no IEND chunk")

    text_data = b"Comment\x00" + FLAG
    chunk_type = b"tEXt"
    crc = zlib.crc32(chunk_type + text_data) & 0xFFFFFFFF
    text_chunk = (
        struct.pack("!I", len(text_data))
        + chunk_type
        + text_data
        + struct.pack("!I", crc)
    )
    return png[:iend_offset] + text_chunk + png[iend_offset:]


def build_network2(image: bytes) -> list[bytes]:
    client_ip = "10.20.30.10"
    server_ip = "10.20.30.80"
    client_mac = "02:00:00:20:30:10"
    server_mac = "02:00:00:20:30:80"
    client_port = 49152
    server_port = 80
    client_isn = 0x10001000
    server_isn = 0x20002000
    frames: list[bytes] = []
    ip_id = 2000

    def add_tcp(
        payload: bytes,
        from_client: bool,
        seq: int,
        ack: int,
        flags: int,
    ) -> None:
        nonlocal ip_id
        if from_client:
            src_ip, dst_ip = client_ip, server_ip
            src_mac, dst_mac = client_mac, server_mac
            src_port, dst_port = client_port, server_port
        else:
            src_ip, dst_ip = server_ip, client_ip
            src_mac, dst_mac = server_mac, client_mac
            src_port, dst_port = server_port, client_port
        tcp = tcp_segment(payload, src_ip, dst_ip, src_port, dst_port, seq, ack, flags)
        packet = ip_packet(tcp, src_ip, dst_ip, 6, ip_id)
        frames.append(ethernet(packet, src_mac, dst_mac))
        ip_id += 1

    # Packets 1-3: TCP handshake.
    add_tcp(b"", True, client_isn, 0, 0x02)
    add_tcp(b"", False, server_isn, client_isn + 1, 0x12)
    add_tcp(b"", True, client_isn + 1, server_isn + 1, 0x10)

    # Packet 4: browser request.
    request = (
        b"GET /catowl.png HTTP/1.1\r\n"
        b"Host: gallery.local\r\n"
        b"User-Agent: CTF-Browser/1.0\r\n"
        b"Accept: image/png\r\n"
        b"Connection: close\r\n\r\n"
    )
    add_tcp(request, True, client_isn + 1, server_isn + 1, 0x18)

    # Packets 5-30: complete HTTP response. The PNG tEXt flag is near the end,
    # so it appears in packet 30 while the exported object remains a valid PNG.
    response_header = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: image/png\r\n"
        + f"Content-Length: {len(image)}\r\n".encode()
        + b"Content-Disposition: inline; filename=catowl.png\r\n"
        b"Connection: close\r\n\r\n"
    )
    response = response_header + image
    segment_count = 26
    base_size, extra = divmod(len(response), segment_count)
    cursor = 0
    server_seq = server_isn + 1
    client_ack = client_isn + 1 + len(request)
    for index in range(segment_count):
        size = base_size + (1 if index < extra else 0)
        payload = response[cursor : cursor + size]
        cursor += size
        flags = 0x19 if index == segment_count - 1 else 0x18
        add_tcp(payload, False, server_seq, client_ack, flags)
        server_seq += len(payload)

    return frames


def main() -> None:
    network1 = build_network1()
    served_image = png_with_flag(ROOT / "catowl.png")
    network2 = build_network2(served_image)
    if len(network1) != 30 or len(network2) != 30:
        raise AssertionError("Each capture must contain exactly 30 packets")

    write_pcap(ROOT / "Network1" / "network1.pcap", network1, 1_788_390_000)
    write_pcap(ROOT / "Network2" / "network2.pcap", network2, 1_788_393_600)


if __name__ == "__main__":
    main()
