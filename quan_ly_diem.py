"""Quản lý điểm thi bằng tệp TXT định dạng JSON, chỉ dùng thư viện chuẩn."""
import json
import math
from pathlib import Path

FILE = Path(__file__).with_name('du_lieu.txt')
TRUONG = ('ma_sv', 'ho_ten', 'ma_mon', 'ten_mon', 'thuong_xuyen', 'giua_ky', 'cuoi_ky')
NHAN = ('Mã sinh viên', 'Họ tên', 'Mã môn', 'Tên môn', 'Điểm thường xuyên', 'Điểm giữa kỳ', 'Điểm cuối kỳ')


def chuan_hoa(ban_ghi):
    if not isinstance(ban_ghi, dict):
        raise ValueError('Bản ghi phải là một đối tượng.')
    kq = {}
    for key in TRUONG[:4]:
        value = ban_ghi.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{key} không được để trống.')
        kq[key] = value.strip()
    for key in TRUONG[4:]:
        value = ban_ghi.get(key)
        if isinstance(value, bool):
            raise ValueError(f'{key} phải là số từ 0 đến 10.')
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(f'{key} phải là số từ 0 đến 10.')
        if not math.isfinite(value) or not 0 <= value <= 10:
            raise ValueError(f'{key} phải là số từ 0 đến 10.')
        kq[key] = value
    return kq


def khoa(r):
    return r['ma_sv'].casefold(), r['ma_mon'].casefold()


def tong(r):
    return round(r['thuong_xuyen'] * 0.2 + r['giua_ky'] * 0.3 + r['cuoi_ky'] * 0.5, 2)


def xep_loai(d):
    if d >= 8.5: return 'Giỏi'
    if d >= 7: return 'Khá'
    if d >= 5: return 'Trung bình'
    return 'Không đạt'


def doc(path=FILE):
    with open(path, encoding='utf-8') as f:
        raw = json.load(f)
    if not isinstance(raw, list):
        raise ValueError('Dữ liệu phải là một danh sách.')
    ds = [chuan_hoa(r) for r in raw]
    if len({khoa(r) for r in ds}) != len(ds):
        raise ValueError('Tệp có khóa mã sinh viên + mã môn bị trùng.')
    return ds


def luu(ds, path=FILE):
    # Ghi tệp tạm trước để tránh mất dữ liệu cũ khi ghi thất bại.
    path = Path(path)
    temp = path.with_name(path.name + '.tmp')
    try:
        with open(temp, 'w', encoding='utf-8') as f:
            json.dump(ds, f, ensure_ascii=False, indent=2, allow_nan=False)
        temp.replace(path)
    finally:
        if temp.exists(): temp.unlink()


def hien_thi(ds):
    if not ds:
        print('Không có bản ghi nào.')
        return
    for i, r in enumerate(ds, 1):
        print(f"{i}. {r['ma_sv']} | {r['ho_ten']} | {r['ma_mon']} | {r['ten_mon']} | "
              f"TX: {r['thuong_xuyen']:.2f} | GK: {r['giua_ky']:.2f} | CK: {r['cuoi_ky']:.2f} | "
              f"Tổng: {tong(r):.2f} | {xep_loai(tong(r))}")


def nhap_ban_ghi(cu=None):
    while True:
        r = {}
        for key, label in zip(TRUONG, NHAN):
            suffix = f" [{cu[key]}] (Enter để giữ)" if cu else ''
            value = input(f'{label}{suffix}: ').strip()
            r[key] = cu[key] if cu and not value else value
        try:
            return chuan_hoa(r)
        except ValueError as e:
            print('Dữ liệu không hợp lệ:', e, 'Vui lòng nhập lại.')


def tim_khoa(ds):
    ma_sv = input('Mã sinh viên: ').strip().casefold()
    ma_mon = input('Mã môn: ').strip().casefold()
    for i, r in enumerate(ds):
        if khoa(r) == (ma_sv, ma_mon): return i
    print('Không tìm thấy bản ghi.')
    return None


def thong_ke(ds):
    if not ds:
        print('Không có dữ liệu để thống kê.')
        return
    diem = [tong(r) for r in ds]
    dat = sum(d >= 5 for d in diem)
    print(f'Tổng số: {len(ds)} | Trung bình: {sum(diem)/len(diem):.2f} | Cao nhất: {max(diem):.2f} | Thấp nhất: {min(diem):.2f}')
    print(f'Đạt: {dat} ({dat/len(ds)*100:.2f}%) | Không đạt: {len(ds)-dat} ({(len(ds)-dat)/len(ds)*100:.2f}%)')
    for loai in ('Giỏi', 'Khá', 'Trung bình', 'Không đạt'):
        print(f'{loai}: {sum(xep_loai(d) == loai for d in diem)}')


def main():
    try:
        ds = doc()
        print(f'Đã đọc {len(ds)} bản ghi từ {FILE}.')
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f'Không đọc được dữ liệu: {e}. Bắt đầu với danh sách trống.')
        ds = []
    dirty = False
    while True:
        print('\n1. Thêm\n2. Hiển thị danh sách\n3. Cập nhật\n4. Xóa\n5. Tìm kiếm\n6. Sắp xếp\n7. Tính toán/Thống kê\n8. Lưu dữ liệu\n9. Đọc dữ liệu\n0. Thoát')
        chon = input('Lựa chọn: ').strip()
        if chon == '1':
            r = nhap_ban_ghi()
            if any(khoa(x) == khoa(r) for x in ds): print('Khóa mã sinh viên + mã môn đã tồn tại.')
            else:
                ds.append(r); dirty = True
                print('Đã thêm bản ghi.')
        elif chon == '2': hien_thi(ds)
        elif chon == '3':
            i = tim_khoa(ds)
            if i is not None:
                r = nhap_ban_ghi(ds[i])
                if any(j != i and khoa(x) == khoa(r) for j, x in enumerate(ds)): print('Khóa mới đã tồn tại.')
                else:
                    ds[i] = r; dirty = True
                    print('Đã cập nhật.')
        elif chon == '4':
            i = tim_khoa(ds)
            if i is not None:
                hien_thi([ds[i]])
                if input('Xác nhận xóa? (y/n): ').strip().casefold() == 'y':
                    ds.pop(i); dirty = True
                    print('Đã xóa.')
                else: print('Đã hủy xóa.')
        elif chon == '5':
            print('1. Mã sinh viên  2. Họ tên  3. Mã môn  4. Tên môn')
            c = input('Chọn: ').strip()
            if c not in ('1', '2', '3', '4'): print('Lựa chọn không hợp lệ.'); continue
            q = input('Từ khóa: ').strip().casefold()
            if not q: print('Từ khóa không được để trống.'); continue
            ket_qua = [r for r in ds if q in r[TRUONG[int(c)-1]].casefold()]
            if ket_qua: hien_thi(ket_qua)
            else: print('Không tìm thấy bản ghi phù hợp.')
        elif chon == '6':
            c = input('1. Điểm tổng kết  2. Họ tên: ').strip()
            if c not in ('1', '2'): print('Lựa chọn không hợp lệ.'); continue
            t = input('1. Tăng dần  2. Giảm dần: ').strip()
            if t not in ('1', '2'): print('Lựa chọn không hợp lệ.'); continue
            ds.sort(key=tong if c == '1' else lambda r: r['ho_ten'].casefold(), reverse=t == '2')
            dirty = True
            hien_thi(ds)
        elif chon == '7': thong_ke(ds)
        elif chon == '8':
            try:
                luu(ds); dirty = False
                print(f'Đã lưu {len(ds)} bản ghi vào {FILE}.')
            except (OSError, ValueError) as e: print('Không thể lưu:', e)
        elif chon == '9':
            if dirty and input('Thay đổi chưa lưu sẽ mất. Tiếp tục đọc? (y/n): ').strip().casefold() != 'y': continue
            try:
                moi = doc(); ds = moi; dirty = False
                print(f'Đã đọc {len(ds)} bản ghi từ {FILE}.')
            except (OSError, ValueError, json.JSONDecodeError) as e: print('Không thể đọc:', e)
        elif chon == '0':
            if dirty and input('Thay đổi chưa lưu sẽ mất. Thoát? (y/n): ').strip().casefold() != 'y': continue
            print('Tạm biệt!'); break
        else: print('Lựa chọn không hợp lệ.')


if __name__ == '__main__':
    try: main()
    except (EOFError, KeyboardInterrupt): print('\nĐã dừng chương trình; thay đổi chưa lưu có thể bị mất.')
