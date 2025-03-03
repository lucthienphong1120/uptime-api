# Uptime-API

Ref: [lucasheld/uptime-kuma-api:latest](https://uptime-kuma-api.readthedocs.io/en/latest/index.html)

## Install

```sh
pip install uptime-kuma-api
```

## Usage

```sh
# python3 api.py -h
usage: api.py [-h] -u HOST [-p PORT] [-a AUTH] [-t TOKEN] [-o OUTPUT] [-i INPUT] [-eT EXPORT_TAGS] [-iT IMPORT_TAGS]
              [-eN EXPORT_NOTIFY] [-iN IMPORT_NOTIFY] [-l] [-d] [-k]

Script IaC Cấu hình Uptime Kuma sử dụng RestAPI

optional arguments:
  -h, --help            show this help message and exit
  -u HOST, --host HOST  IP của Host Uptime Kuma (VD: 127.0.0.1)
  -p PORT, --port PORT  Chỉ định Port của Uptime Kuma (Default: 3001)
  -a AUTH, --auth AUTH  Đường dẫn đến file xác thực username:password (VD: auth.txt)
  -t TOKEN, --token TOKEN
                        Chỉ định file chứa token (VD: token_ip.txt)
  -o OUTPUT, --output OUTPUT
                        Xuất danh sách Monitor ra file JSON (VD: monitors.json)
  -i INPUT, --input INPUT
                        Nhập danh sách Monitor từ file JSON (VD: monitors.json)
  -eT EXPORT_TAGS, --export-tags EXPORT_TAGS
                        Xuất danh sách Tags ra file JSON (VD: tags.json)
  -iT IMPORT_TAGS, --import-tags IMPORT_TAGS
                        Nhập danh sách Tags từ file JSON (VD: tags.json)
  -eN EXPORT_NOTIFY, --export-notify EXPORT_NOTIFY
                        Xuất danh sách Notify ra file JSON (VD: notify.json)
  -iN IMPORT_NOTIFY, --import-notify IMPORT_NOTIFY
                        Nhập danh sách Notify từ file JSON (VD: notify.json)
  -l, --list            Liệt kê danh sách Monitor
  -d, --delete          Xóa tất cả các Monitor
  -k, --clean-up        Dọn dẹp dữ liệu (events, heartbeats, stats)
```
