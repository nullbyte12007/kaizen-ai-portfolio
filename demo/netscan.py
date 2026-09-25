#!/usr/bin/env python3
"""
netscan — network / port scanner (Python stdlib only, no dependencies).

Hanya untuk jaringan yang KAMU miliki atau punya izin untuk memindai.
Target non-privat (IP publik) wajib pakai --authorized.

Contoh:
  ./netscan.py 192.168.0.0/24
  ./netscan.py 192.168.0.0/24 --ports common
  ./netscan.py 10.11.12.4 10.11.12.7 --ports 22,80,443,5432 --banner
  ./netscan.py 100.64.0.0/24 --fast            # discovery doang
  ./netscan.py 192.168.0.0/24 --ports 1-1024 --json out.json
  ./netscan.py --hosts-file targets.txt --csv hasil.csv
"""
from __future__ import annotations

import argparse
import csv
import ipaddress
import json
import socket
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

COMMON_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns", 80: "http",
    110: "pop3", 135: "msrpc", 139: "netbios", 143: "imap", 161: "snmp",
    443: "https", 445: "smb", 1433: "mssql", 1521: "oracle", 1883: "mqtt",
    2049: "nfs", 3000: "http-alt", 3306: "mysql", 3389: "rdp", 5432: "postgres",
    5672: "amqp", 5900: "vnc", 6379: "redis", 8000: "http-alt",
    8080: "http-alt", 8443: "https-alt", 8888: "http-alt", 9000: "minio/s3",
    9092: "kafka", 9200: "elastic", 9300: "elastic", 11211: "memcached",
    27017: "mongodb",
}
# port yang dipakai buat "host is up?" kalau ICMP nggak tersedia
DISCOVERY_PORTS = (80, 443, 22, 445, 8080, 3389)
TIMEOUT = 1.0


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def parse_ports(spec: str | None) -> list[int]:
    if not spec:
        return []
    spec = spec.strip().lower()
    if spec in ("common", "default"):
        return sorted(COMMON_PORTS)
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(part))
    bad = [p for p in out if not (0 < p < 65536)]
    if bad:
        raise SystemExit(f"port tidak valid: {bad}")
    return sorted(out)


def expand_targets(args) -> list[str]:
    targets: list[str] = []
    for t in args.targets or []:
        t = t.strip()
        if not t:
            continue
        if "/" in t:
            net = ipaddress.ip_network(t, strict=False)
            targets.extend(str(ip) for ip in net.hosts())
        elif "-" in t and t.replace(".", "").replace("-", "").isdigit():
            # bentuk range sederhana: 192.168.0.10-20
            base, last = t.rsplit(".", 1)
            a, b = last.split("-", 1)
            targets.extend(f"{base}.{i}" for i in range(int(a), int(b) + 1))
        else:
            targets.append(t)
    if args.hosts_file:
        with open(args.hosts_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.split("#", 1)[0].strip()
                if line:
                    if "/" in line:
                        targets.extend(str(ip) for ip in ipaddress.ip_network(line, strict=False).hosts())
                    else:
                        targets.append(line)
    # unik, urut
    seen: set[str] = set()
    uniq: list[str] = []
    for t in targets:
        try:
            ip = str(ipaddress.ip_address(t))
        except ValueError:
            log(f"lewati target tidak valid: {t}")
            continue
        if ip not in seen:
            seen.add(ip)
            uniq.append(ip)
    return uniq


def icmp_ping(ip: str, timeout: float) -> bool | None:
    """True/False kalau ping tersedia, None kalau nggak ada binary ping."""
    for cmd in (["ping", "-c", "1", "-W", str(max(1, int(timeout)))],
                ["ping", "-c", "1", str(ip)]):
        try:
            res = subprocess.run(cmd + [ip], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            return res.returncode == 0
        except FileNotFoundError:
            continue
        except Exception:
            break
    return None


def tcp_open(ip: str, port: int, timeout: float) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        return s.connect_ex((ip, port)) == 0


def grab_banner(ip: str, port: int, timeout: float) -> str:
    try:
        with socket.create_connection((ip, port), timeout=timeout) as s:
            s.settimeout(timeout)
            if port in (80, 8080, 8000, 8888, 3000, 9000):
                s.sendall(f"HEAD / HTTP/1.0\r\nHost: {ip}\r\n\r\n".encode())
            try:
                data = s.recv(200)
            except socket.timeout:
                return ""
            return data.decode("utf-8", "replace").strip().splitlines()[0][:100] if data else ""
    except Exception:
        return ""


def scan_host(ip: str, ports: list[int], timeout: float, do_banner: bool,
              threads: int) -> tuple[bool | None, list[tuple[int, str]]]:
    if not ports:
        # cuma discovery
        for p in DISCOVERY_PORTS:
            if tcp_open(ip, p, timeout):
                return True, []
        return icmp_ping(ip, timeout), []

    open_ports: list[tuple[int, str]] = []
    with ThreadPoolExecutor(max_workers=min(threads, max(1, len(ports)))) as ex:
        futs = {ex.submit(tcp_open, ip, p, timeout): p for p in ports}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                if fut.result():
                    open_ports.append((p, COMMON_PORTS.get(p, "?")))
            except Exception:
                pass
    open_ports.sort()
    if open_ports:
        if do_banner:
            open_ports = [(p, f"{svc} {grab_banner(ip, p, timeout)}".strip()) for p, svc in open_ports]
        return True, open_ports
    # nggak ada port kebuka -> tetap cek ICMP biar tau host hidup atau nggak
    return icmp_ping(ip, timeout), []


def main() -> int:
    ap = argparse.ArgumentParser(description="netscan — port/host scanner (authorized use only)",
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="*", help="IP, CIDR (192.168.0.0/24), atau range (192.168.0.10-20)")
    ap.add_argument("--hosts-file", help="file berisi daftar target (1 per baris, # untuk komentar)")
    ap.add_argument("-p", "--ports", default="", help="'common', daftar (22,80,443) atau range (1-1024). kosong = discovery saja")
    ap.add_argument("--fast", action="store_true", help="discovery saja (tanpa port scan)")
    ap.add_argument("--banner", action="store_true", help="ambil banner service dari port yang terbuka")
    ap.add_argument("-t", "--timeout", type=float, default=TIMEOUT, help="timeout per koneksi (detik, default 1.0)")
    ap.add_argument("--threads", type=int, default=200, help="jumlah worker (default 200)")
    ap.add_argument("--json", dest="json_out", help="simpan hasil ke file JSON")
    ap.add_argument("--csv", dest="csv_out", help="simpan hasil ke file CSV")
    ap.add_argument("--authorized", action="store_true",
                    help="konfirmasi bahwa kamu berhak memindai target non-privat")
    args = ap.parse_args()

    targets = expand_targets(args)
    if not targets:
        ap.error("tidak ada target. contoh: netscan.py 192.168.0.0/24")

    public = [ip for ip in targets if not ipaddress.ip_address(ip).is_private]
    if public and not args.authorized:
        log(f"!! {len(public)} target NON-PRIVAT terdeteksi (mis. {public[0]}).")
        log("   Scan hanya boleh dilakukan pada aset yang kamu miliki/punya izin.")
        log("   Kalau memang berizin, ulangi dengan --authorized")
        return 2

    ports = [] if args.fast else parse_ports(args.ports)
    log(f"target: {len(targets)} host | port: {'discovery' if not ports else len(ports)} "
        f"| timeout: {args.timeout}s | threads: {args.threads}")

    results = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=min(args.threads, max(1, len(targets)))) as ex:
        futs = {ex.submit(scan_host, ip, ports, args.timeout, args.banner, args.threads): ip
                for ip in targets}
        done = 0
        for fut in as_completed(futs):
            ip = futs[fut]
            done += 1
            try:
                up, open_ports = fut.result()
            except Exception as e:
                up, open_ports = None, []
                log(f"{ip}: error {e}")
            if up or open_ports:
                results.append({"ip": ip,
                                "status": "up" if up else "open-ports-only",
                                "open_ports": [{"port": p, "service": s} for p, s in open_ports]})
            if done % 25 == 0:
                log(f"  ...{done}/{len(targets)}")

    dt = time.time() - t0
    results.sort(key=lambda r: ipaddress.ip_address(r["ip"]))

    print(f"\n=== HASIL ({len(results)} host merespons dari {len(targets)}) — {dt:.1f}s ===")
    print(f"{'IP':<16} {'STATUS':<16} OPEN PORTS")
    print("-" * 72)
    for r in results:
        plist = ", ".join(f"{p['port']}/{p['service']}" for p in r["open_ports"]) or "-"
        print(f"{r['ip']:<16} {r['status']:<16} {plist}")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump({"targets": len(targets), "elapsed_s": round(dt, 2), "results": results},
                      fh, indent=2)
        log(f"JSON -> {args.json_out}")
    if args.csv_out:
        with open(args.csv_out, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["ip", "status", "open_ports"])
            for r in results:
                w.writerow([r["ip"], r["status"],
                            ";".join(f"{p['port']}/{p['service']}" for p in r["open_ports"])])
        log(f"CSV -> {args.csv_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
