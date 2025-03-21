from uptime_kuma_api import UptimeKumaApi
import getpass
import json
import os
import argparse

# Hàm đọc file auth
def read_auth_file(auth_file):
    try:
        with open(auth_file, "r", encoding="utf-8") as f:
            line = f.readline().strip()
            if ":" not in line:
                raise ValueError("File auth không hợp lệ! Định dạng đúng: user:pass")
            username, password = line.split(":", 1)
            return username.strip(), password.strip()
    except Exception as e:
        print(f"[x] Lỗi khi đọc file auth: {e}")
        username = input("Nhập Username: ")
        password = getpass.getpass("Nhập Password: ")
        return username.strip(), password.strip()

# Hàm lưu token vào file
def save_token(token, token_file=None):
    with open(token_file, "w") as f:
        f.write(token)

# Hàm tải token từ file
def load_token(token_file=None):
    if os.path.exists(token_file):
        with open(token_file, "r") as f:
            return f.read().strip()
    else:
        print(f"[!] Không tìm thấy file {token_file}")
    return None

# Hàm hiển thị thông tin phiên bản
def show_app_info(api):
    try:
        print("[+] Hiển thị thông tin phiên bản")
        info = api.info()
        print(f"  - Version: {info['version']} | Lastest: {info['latestVersion']} | Container: {info['isContainer']}")
        print(f"  - Database: {info['dbType']} | Timezone: {info['serverTimezone']} UTC{info['serverTimezoneOffset']}")
        print(f"  - App URL: {info['primaryBaseURL']}")
    except Exception as e:
        print(f"[!] Lỗi khi lấy thông tin phiên bản: {e}")

# Hàm liệt kê danh sách monitor
def list_monitors(monitors):
    for monitor in monitors:
        print(f"  - ID: {monitor['id']} | Tên: {monitor['name']} | Active: {monitor['active']}")

# Hàm xuất thông tin monitor ra JSON
def export_monitors(monitors, filename="monitors.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(monitors, f, indent=4, ensure_ascii=False)
        print(f"[✔] Danh sách Monitor đã được lưu vào: {filename}")
    except Exception as e:
        print(f"[!] Lỗi khi xuất danh sách Monitor: {e}")

# Hàm xuất thông tin monitor tags
def export_tags(api, filename="tags.json"):
    try:
        tags = api.get_tags()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(tags, f, indent=4, ensure_ascii=False)
        print(f"[✔] Đã xuất {len(tags)} tags vào {filename}")
    except Exception as e:
        print(f"[x] Lỗi khi export tags: {e}")

# Hàm nhập monitor tags từ JSON
def import_tags(api, filename="tags.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            tags_to_add = json.load(f)

        existing_tags = {tag["name"]: tag for tag in api.get_tags()}  # Lấy danh sách tag hiện có

        for tag in tags_to_add:
            if tag["name"] in existing_tags:
                print(f"[!] Tag '{tag['name']}' đã tồn tại: Bỏ qua")
                continue  # Bỏ qua nếu tag đã tồn tại
            try:
                api.add_tag(name=tag["name"], color=tag["color"])
                print(f"[✔] Đã thêm tag: {tag['name']}")
            except Exception as e:
                print(f"[x] Lỗi khi thêm tag '{tag['name']}': {e}") 
    except Exception as e:
        print(f"[x] Lỗi khi import tags: {e}")

# Hàm xuất thông tin notification
def export_notify(api, filename="notify.json"):
    try:
        notify = api.get_notifications()
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(notify, f, indent=4, ensure_ascii=False)
        print(f"[✔] Đã xuất danh sách Notify ra {filename}")
    except Exception as e:
        print(f"[x] Lỗi khi xuất Notify: {e}")

# Hàm nhập notification từ JSON
def import_notify(api, filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            notify_to_add = json.load(f)

        existing_notify = {notify["name"]: notify for notify in api.get_notifications()}  # Lấy danh sách notify hiện có

        for notify in notify_to_add:
            if notify["name"] in existing_notify:
                print(f"[!] Notify '{notify['name']}' đã tồn tại: Bỏ qua")
                continue  # Bỏ qua nếu notify đã tồn tại
            try:
                # Chỉ nhập loại Telegram
                if notify["type"] == "telegram":
                    api.add_notification(
                        name=notify["name"],
                        type="telegram",
                        isDefault=notify.get("isDefault", False),
                        applyExisting=notify.get("applyExisting", False),
                        telegramChatID=notify.get("telegramChatID", ""),
                        telegramSendSilently=notify.get("telegramSendSilently", False),
                        telegramProtectContent=notify.get("telegramProtectContent", False),
                        telegramMessageThreadID=notify.get("telegramMessageThreadID", ""),
                        telegramBotToken=notify.get("telegramBotToken", ""),
                    )
                    print(f"[✔] Đã thêm Notify: {notify['name']}")
                else:
                    print("[!] Chỉ hỗ trợ nhập Notification dạng Telegram")
            except Exception as e:
                print(f"[x] Lỗi khi thêm notify '{notify['name']}': {e}")
    except Exception as e:
        print(f"[x] Lỗi khi nhập Notify: {e}")

# Hàm nhập Monitor từ JSON
def import_monitors(api, monitors, filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            imported_monitors = json.load(file)

        print(f"[+] Đang thêm {len(imported_monitors)} Monitor từ {filename}...")

        # Lấy danh sách pathName hiện có
        existing_monitors = {monitor.get("name") for monitor in monitors}

        handle_import_monitors(api, imported_monitors, existing_monitors)
    except Exception as e:
        print(f"[!] Lỗi khi đọc file {filename}: {e}")

# Hàm xử lý nhập Monitor parent-child
# Lưu ý: Việc import monitors phụ thuộc vào các khóa ngoại: parent, notification, tags
def handle_import_monitors(api, monitors_to_add, existing_monitors):
    added_monitors = {}  # Lưu mapping { "name" -> new_id } sau khi thêm thành công
    json_id_to_name = {}  # Mapping { json_id -> json_name } để tra cứu tên

    # Tạo mapping { json_id -> json_name } từ file JSON
    for monitor in monitors_to_add:
        if "id" in monitor and "name" in monitor:
            json_id_to_name[monitor["id"]] = monitor["name"]

    child_queue = []
    # Thêm monitor **KHÔNG CÓ parent** trước, lưu mapping {name -> id}
    # -> vì id group và id monitor là không đoán trước được nên không map được ràng buộc như trong file json
    # -> vòng lặp đầu cần import các parent trước (parentid=none) và trả về mapping name:id
    print("[+] Xử lý nhập các Parent Monitor từ json (không phụ thuộc):")
    child_queue, added_monitors = add_parent_monitors(api, monitors_to_add, existing_monitors, added_monitors, child_queue)

    # Thêm các monitor có parent **sau khi parent đã tồn tại**
    # -> lookup parent id trong json ra parent name trong json
    # -> từ parent name trong json lại lookup ra parent id mới trong mapping ở trên
    # -> gán parent id cho monitor con dựa trên mapping mới
    print(f"[+] Xử lý nhập các Child Monitor từ json (còn {len(child_queue)}):")
    added_monitors = add_child_monitors(api, child_queue, json_id_to_name, added_monitors)

    print(f"[✔] Đã thêm {len(added_monitors)} Monitor")

    # Thêm Tag cho Monitor
    print("[+] Xử lý nhập tags cho monitors...")
    add_monitor_tags(api, monitors_to_add, added_monitors)

def add_parent_monitors(api, monitors_to_add, existing_monitors, added_monitors, child_queue):
    for monitor in monitors_to_add:
        if monitor.get("name") in existing_monitors:
            print(f"[!] Monitor {monitor.get('name')} đã tồn tại: Bỏ qua")
            continue  # Bỏ qua monitor đã tồn tại

        if not monitor.get("parent"):  # Monitor không có parent
            monitor_id = add_monitor(api, monitor, None)  # Parent ID = None
            if monitor_id:
                added_monitors[monitor.get("name")] = monitor_id  # Lưu ID vào mapping
        else:
            child_queue.append(monitor)  # Monitor có parent sẽ xử lý sau
    return child_queue, added_monitors

def add_child_monitors(api, child_queue, json_id_to_name, added_monitors):
    while child_queue:
        remaining_queue = []
        for monitor in child_queue:
            json_parent_id = monitor.get("parent")  # Lấy parent_id từ JSON
            parent_name = json_id_to_name.get(json_parent_id)  # Tìm parent name từ JSON
            parent_id = added_monitors.get(parent_name)  # Lấy parent_id mới sau khi import

            if parent_id:
                monitor_id = add_monitor(api, monitor, parent_id)  # Gán parent_id thực tế
                if monitor_id:
                    added_monitors[monitor.get("name")] = monitor_id  # Lưu ID mới
            else:
                print(f"[!] Chưa tìm thấy parent_id hợp lệ cho {monitor.get('name')}")
                remaining_queue.append(monitor)  # Nếu chưa có parent, đẩy vào lại hàng đợi

        # Nếu không có tiến triển, dừng vòng lặp để tránh lặp vô hạn
        if len(remaining_queue) == len(child_queue):
            print("[x] Lỗi: Một số monitor có parent không tồn tại trong JSON!")
            break
        child_queue = remaining_queue
    return added_monitors

def add_monitor_tags(api, monitors_to_add, added_monitors):
    # Lấy danh sách tag hiện có từ API và tạo mapping { name -> tag_id }
    existing_tags = {tag["name"]: tag["id"] for tag in api.get_tags()}
    if not existing_tags:
        print("[!] Không có tag nào trong hệ thống, vui lòng nhập Tag và thử lại")
        return

    for monitor in monitors_to_add:
        monitor_name = monitor["name"]
        monitor_id = added_monitors.get(monitor_name)

        if not monitor_id:
            continue

        for tag in monitor.get("tags", []):
            tag_name = tag["name"]
            tag_id = existing_tags.get(tag_name)

            if not tag_id:
                print(f"[x] Lỗi: Tag '{tag_name}' không tồn tại, vui lòng import tag trước")
                continue
            try:
                api.add_monitor_tag(tag_id=tag_id, monitor_id=monitor_id, value=tag.get("value", ""))
                print(f"[✔] Gán tag {tag_name} (ID: {tag_id}) vào monitor {monitor_name}")
            except Exception as e:
                print(f"[x] Lỗi khi gán tag {tag_name} (ID: {tag_id}) vào {monitor_name}: {e}")

# Hàm hỗ trợ thêm một monitor
def add_monitor(api, monitor, parent_id):
    monitor_id = None
    try:
        result = api.add_monitor(
            name=monitor.get("name", ""),
            description=monitor.get("description", None),
            type=monitor.get("type", "http"),
            parent=parent_id, # Gán ID parent thực tế
            url=monitor.get("url", ""),
            method=monitor.get("method", "GET"),
            hostname=monitor.get("hostname", None),
            port=monitor.get("port", None),
            maxretries=monitor.get("maxretries", 0),
            timeout=monitor.get("timeout", 48),
            interval=monitor.get("interval", 60),
            retryInterval=monitor.get("retryInterval", 60),
            resendInterval=monitor.get("resendInterval", 0),
            expiryNotification=monitor.get("expiryNotification", False),
            ignoreTls=monitor.get("ignoreTls", False),
            upsideDown=monitor.get("upsideDown", False),
            packetSize=monitor.get("packetSize", 56),
            maxredirects=monitor.get("maxredirects", 10),
            accepted_statuscodes=monitor.get("accepted_statuscodes", ["200-299"]),
            dns_resolve_type=monitor.get("dns_resolve_type", "A"),
            dns_resolve_server=monitor.get("dns_resolve_server", "1.1.1.1"),
            notificationIDList=monitor.get("notificationIDList", []),
        )
        monitor_id = result['monitorID']
        print(f"[✔] Đã thêm Monitor: {monitor.get('name')} ({monitor_id})")
        return monitor_id
    except Exception as e:
        if "a foreign key constraint fails" in str(e):
            print(f"[x] Lỗi khi thêm Monitor {monitor.get('name')}: ", end="")
            if "monitor_notification" in str(e):
                print("Thiếu ràng buộc notifications, vui lòng thêm notify trước")

            exit(1)
        else:
            print(f"[x] Lỗi khi thêm Monitor {monitor.get('name')}: {e}")
        return None

# Hàm xóa tất cả monitor
def delete_all_monitors(api, monitors):
    confirm = input("[+] Bạn có chắc chắn muốn xóa tất cả Monitor? (y/N): ").strip().lower()
    if confirm == 'y':
        total = len(monitors)
        deleted_count = 0
        for monitor in monitors:
            try:
                api.delete_monitor(monitor["id"])
                deleted_count += 1
                # In trạng thái cập nhật trên cùng một dòng
                print(f"[+] Đã xóa {deleted_count}/{total} | Monitor: {monitor.get('name')}")
            except Exception as e:
                print(f"[!] Lỗi khi xóa Monitor {monitor.get('name')}: {e}")
        print("[✔] Tất cả Monitor đã được xóa thành công.")
    else:
        print("[!] Đã hủy thao tác xóa Monitor!")
        return

# Hàm dọn dẹp tất cả các thống kê
def clean_up(api, monitors):
    try:
        for monitor in monitors:
            monitor_id = monitor["id"]
            monitor_name = monitor["name"]

            # Xóa sự kiện (events)
            api.clear_events(monitor_id)
            print(f"[✔] Đã xóa Events cho Monitor: {monitor_name}")

            # Xóa heartbeat
            api.clear_heartbeats(monitor_id)
            print(f"[✔] Đã xóa Heartbeats cho Monitor: {monitor_name}")

        # Xóa toàn bộ thống kê
        api.clear_statistics()
        print("[✔] Đã xóa toàn bộ thống kê trong Uptime Kuma!")

    except Exception as e:
        print(f"[x] Lỗi khi dọn dẹp dữ liệu: {e}")

# Hàm xử lý chính
def main(args):
    try:
        # Thiết lập các tham số
        URL = f"http://{args.host}:{args.port}"
        token_file = f"token_{args.host}_{args.port}.txt"
        # Kiểm tra nếu có tham số -t
        if args.token:
            token_file = args.token

        # Kết nối tới API Uptime Kuma
        print(f"[+] Đang kết nối tới Uptime Kuma: {URL}")
        api = UptimeKumaApi(URL, timeout=120)

        # Thử tải token từ file
        print("[+] Kiểm tra session token hiện có")
        token = load_token(token_file)
        if token:
            print("[+] Token tồn tại, tiến hành đăng nhập bằng token")
            print(f"[+] Sử dụng Token file: {token_file}")
            try:
                api.login_by_token(token)
                print("[✔] Đăng nhập bằng token thành công!")
            except Exception as e:
                print(f"[!] Lỗi khi đăng nhập bằng token: {e}")
                token = None

        # Đăng nhập bằng userpass
        if not token and args.auth:
            print("[+] Chưa có thông tin token trước đó, đăng nhập bằng userpass")
            print(f"[+] Sử dụng Auth file: {args.auth}")
            username, password = read_auth_file(args.auth)
            try:
                auth = api.login(username, password)
                print("[✔] Đăng nhập bằng userpass thành công!")
                # Lưu token sau khi đăng nhập thành công
                save_token(auth['token'], token_file)
                print("[+] Đã lưu token sử dụng cho lần sau")
            except Exception as e:
                print(f"[x] Lỗi khi đăng nhập bằng userpass: {e}")
                return

        # Hiển thị thông tin phiên bản
        show_app_info(api)

        # Kiểm tra danh sách Monitor hiện có
        print("[+] Kiểm tra danh sách Monitor hiện có")
        monitors = []
        try:
            monitors = api.get_monitors()
            # Nếu có tham số -l thì hiển thị danh sách Monitor
            if args.list:
                list_monitors(monitors)
            else:
                print(f"  - Tổng cộng: {len(monitors)} Monitor")
        except Exception as e:
            print(f"[!] Lỗi khi lấy danh sách Monitor: {e}")

        # Nếu có tham số -eA thì lưu Notify, Tags, Monitor ra JSON
        if args.export_all:
            confirm = input("[+] Xuất ra các file: notify.json, tags.json, monitors.json? (y/N): ").strip().lower()
            if confirm == 'y':
                export_notify(api, "notify.json")
                export_tags(api, "tags.json")
                export_monitors(monitors, "monitors.json")

        # Nếu có tham số -iA thì nhập Notify, Tags, Monitor từ JSON
        if args.import_all:
            confirm = input("[+] Chuẩn bị các file: notify.json, tags.json, monitors.json? (y/N): ").strip().lower()
            if confirm == 'y':
                import_notify(api, "notify.json")
                import_tags(api, "tags.json")
                import_monitors(api, monitors, "monitors.json")

        # Nếu có tham số -eM thì lưu danh sách Monitor vào file JSON
        if args.export_monitor:
            export_monitors(monitors, args.export_monitor)

        # Nếu có tham số -iM, nhập Monitor từ file JSON
        if args.import_monitor:
            import_monitors(api, monitors, args.import_monitor)

        # Nếu có tham số --export-tags, xuất danh sách tag ra file JSON
        if args.export_tags:
            export_tags(api, args.export_tags)

        # Nếu có tham số --import-tags, nhập danh sách tag từ file JSON
        if args.import_tags:
            import_tags(api, args.import_tags)

        # Nếu có tham số --export-notify, xuất danh sách notify ra file JSON
        if args.export_notify:
            export_notify(api, args.export_notify)

        # Nếu có tham số --import-notify, nhập danh sách notify từ file JSON
        if args.import_notify:
            import_notify(api, args.import_notify)

        # Nếu có tham số -i, xóa các Monitor hiện có
        if args.delete:
            delete_all_monitors(api, monitors)

        # Nếu có tham số --clean-up, thực hiện dọn dẹp dữ liệu
        if args.clean_up:
            clean_up(api, monitors)

    except Exception as e:
        print(f"[x] Lỗi kết nối tới Uptime Kuma: {e}")

    finally:
        # Đảm bảo ngắt kết nối API sau khi chạy xong
        try:
            api.disconnect()
            print("[✔] Đã ngắt kết nối API.")
        except Exception as e:
            print(f"[x] Lỗi khi ngắt kết nối: {e}")

# Chạy chương trình chính
if __name__ == "__main__":
    # Xử lý tham số dòng lệnh
    parser = argparse.ArgumentParser(description="Script IaC Cấu hình Uptime Kuma sử dụng RestAPI")
    parser.add_argument("-u", "--host", type=str, help="IP của Host Uptime Kuma (VD: 127.0.0.1)", required=True)
    parser.add_argument("-p", "--port", type=str, help="Chỉ định Port của Uptime Kuma (Default: 3001)", default="3001")
    parser.add_argument("-a", "--auth", type=str, help="Đường dẫn đến file xác thực username:password (Default: auth.txt)", default="auth.txt")
    parser.add_argument("-t", "--token", type=str, help="Chỉ định file chứa token (Default: token_ip.txt)", default=None)
    parser.add_argument("-eA", "--export-all", action="store_true", help="Xuất toàn bộ Monitor/Notify/Tags ra filename mặc định")
    parser.add_argument("-iA", "--import-all", action="store_true", help="Nhập toàn bộ Monitor/Notify/Tags từ filename mặc định")
    parser.add_argument("-eM", "--export-monitor", type=str, help="Xuất danh sách Monitor ra file JSON (VD: monitors.json)")
    parser.add_argument("-iM", "--import-monitor", type=str, help="Nhập danh sách Monitor từ file JSON (VD: monitors.json)")
    parser.add_argument("-eT", "--export-tags", type=str, help="Xuất danh sách Tags ra file JSON (VD: tags.json)")
    parser.add_argument("-iT", "--import-tags", type=str, help="Nhập danh sách Tags từ file JSON (VD: tags.json)")
    parser.add_argument("-eN", "--export-notify", type=str, help="Xuất danh sách Notify ra file JSON (VD: notify.json)")
    parser.add_argument("-iN", "--import-notify", type=str, help="Nhập danh sách Notify từ file JSON (VD: notify.json)")
    parser.add_argument("-l", "--list", action="store_true", help="Liệt kê danh sách Monitor")
    parser.add_argument("-d", "--delete", action="store_true", help="Xóa tất cả các Monitor")
    parser.add_argument("-k", "--clean-up", action="store_true", help="Dọn dẹp dữ liệu (events, heartbeats, stats)")
    args = parser.parse_args()
    
    # Kiểm tra các tham số sau không được conflict
    selected_options = sum(bool(arg) for arg in [args.export_all, args.import_all, args.export_monitor, args.import_monitor, args.list, args.delete, args.export_tags, args.import_tags, args.export_notify, args.import_notify, args.clean_up])
    if selected_options > 1:
        print("[x] Lỗi: Chỉ được phép sử dụng **một** trong các tham số!")
        exit(1)

    main(args)
