# Hướng dẫn nhanh — 15 phút

Một tour ngắn, thẳng thắn qua `vibecodekit-mql5-ea`. Sau bài này bạn sẽ scaffold
một EA MQL5 mới, chạy lint + cổng pre-deploy, và hiểu mỗi cổng thực sự đang đo
cái gì.

> 🇬🇧 English version: [`QUICKSTART.md`](QUICKSTART.md)

> **Tiết lộ về heuristic.** `Trader-17`, ma trận chất lượng `8×8`, các ID
> anti-pattern `AP-XX`, và các persona `RRI` đều là **heuristic do dự án này tự
> định nghĩa**. Đây là guardrail có chủ kiến — **không phải chuẩn ngành**, không
> phải chứng nhận, không thay thế được validation trên tài khoản live. Hãy xử
> lý chúng đúng tinh thần đó.

---

## 0. Yêu cầu (2 phút)

- Python ≥ 3.10
- `git` + một shell

Tùy chọn (cho compile MQL5 thực):

- Wine + một bản `metaeditor64.exe` nằm trên `PATH` (kit báo
  `MetaEditor not found — skipped (non-blocking)` khi thiếu, các cổng còn lại
  vẫn chạy).

---

## 1. Cài kit (1 phút)

```bash
git clone https://github.com/VibeMql5Codekit/vibecodekit-mql5-ea.git
cd vibecodekit-mql5-ea
pip install -e ".[dev]"
```

Kiểm tra:

```bash
mql5-build --list
```

Bạn sẽ thấy ~17 scaffold preset:

![mql5-build --list](quickstart/img/01-build-list.png)

---

## 2. Scaffold một EA mới (1 phút)

```bash
mql5-build \
  --preset stdlib \
  --stack netting \
  --name SampleEA \
  --output ./out
```

Output:

```
Rendered stdlib/netting -> ./out/SampleEA
```

Mở `./out/SampleEA/SampleEA.mq5`. File đã sẵn:

- `CPipNormalizer` (pip cross-broker: 5d EURUSD, 4d USDJPY, 3d XAUUSD-Exness, 2d XAUUSD-ICM)
- `CRiskGuard` (giới hạn lỗ hằng ngày + max-positions)
- `CMagicRegistry` (chống va đập magic number giữa các EA cùng symbol)
- `CTrade` từ standard library của MetaTrader

Khối strategy được để trống có chủ ý:

```cpp
bool buySignal  = false;  // Thay bằng điều kiện buy của bạn
bool sellSignal = false;  // Thay bằng điều kiện sell của bạn
```

Đây là chỉnh sửa bắt buộc duy nhất. Thay 2 biến này bằng signal thật.

---

## 3. Lint scaffold (1 phút)

```bash
mql5-lint ./out/SampleEA/SampleEA.mq5
```

Bạn sẽ thấy 0 lỗi critical và 4 warning placeholder:

![mql5-lint output](quickstart/img/02-lint.png)

Warning là artifact của template (chưa có trailing stop, chưa retry, chưa
comment trên trade). Chúng không block cổng; bạn có thể xử lý sau.

> **Linter KHÔNG làm gì.** Nó dựa trên regex. Rule AP-05 ("> 6 inputs") là
> mặc định có chủ kiến và sẽ false-positive trên EA grid / portfolio hợp lệ.
> Sửa trực tiếp `scripts/vibecodekit_mql5/lint.py` nếu cần điều chỉnh ngưỡng.

---

## 4. Chạy checklist Trader-17 (1 phút)

```bash
mql5-trader-check --ea ./out/SampleEA/SampleEA.mq5
```

Trên scaffold trắng, bạn sẽ thấy đại loại:

![mql5-trader-check](quickstart/img/03-trader-check.png)

`11 / 17 PASS, 6 N-A` — cổng **fail** (yêu cầu ≥ 15 PASS). Các mục `N-A`
(T08–T11, T04, T06) cần bằng chứng external mà kit không suy ra được từ source:
walk-forward, Monte Carlo, multi-broker, overfit, news filter, spread guard.
Bổ sung bằng `mql5-walkforward`, `mql5-monte-carlo`, `mql5-multibroker`, v.v.
sau khi có report backtest.

> **Lưu ý thẳng.** Trader-17 là checklist do dự án tự định nghĩa, không phải
> chứng nhận ngành. Ngưỡng trong `scripts/vibecodekit_mql5/trader_check.py`
> phản ánh quan điểm của kit về vệ sinh tối thiểu cho EA bán lẻ.

---

## 5. Chạy cổng permission (2 phút)

```bash
mql5-permission --ea ./out/SampleEA/SampleEA.mq5 --mode PERSONAL
```

Bạn sẽ thấy report fail-fast:

![mql5-permission](quickstart/img/04-permission.png)

Pipeline chạy layer theo thứ tự và dừng ngay layer đầu tiên fail. Mode quyết
định layer nào chạy:

| Mode | Layers | Mục đích |
|---|---|---|
| `PERSONAL` | 1, 2, 3, 4, 7 | Cổng nhẹ cho solo dev |
| `TEAM` | 1, 2, 3, 4, 5, 7 | Thêm layer methodology |
| `ENTERPRISE` | 1, 2, 3, 4, 5, 6, 7 | Thêm ma trận chất lượng 8×8 |

Scaffold trắng **được mong đợi fail** ở layer 4 — đó chính là mục đích của
cổng. Muốn PASS, bạn cần strategy thật + bằng chứng backtest; kit sẽ không
chứng nhận template rỗng.

Output máy-đọc-được:

```bash
mql5-permission --ea ./out/SampleEA/SampleEA.mq5 --mode PERSONAL --json
```

---

## 6. Lặp (≈ 10 phút)

Vòng lặp thực tế:

1. Sửa `OnTick` trong `SampleEA.mq5` để tính `buySignal` / `sellSignal`.
2. Chạy lại `mql5-lint` — xử lý critical mới (nếu có).
3. Compile bằng MetaEditor (hoặc `mql5-compile` nếu có trên `PATH`).
4. Backtest trong Strategy Tester của MT5; export report XML.
5. Đẩy report qua `mql5-backtest`, `mql5-walkforward`, `mql5-monte-carlo`.
6. Chạy lại `mql5-trader-check` và `mql5-permission` cho tới khi cổng pass ở
   mode bạn nhắm.

Để xem snapshot cụ thể và tái tạo được mỗi cổng output gì trên EA scaffold mới
nhất, xem [`reference-ea/REPORT.md`](reference-ea/REPORT.md).

---

## Tiếp theo

- **AI coding agents (Devin, Claude Code, Cursor, Codex):** đọc
  [`/AGENTS.md`](../AGENTS.md) trước khi sửa code.
- **Nhập strategy từ ý tưởng tự do:** xem Prompt Architect schema trong
  [`prompt-architect/README.md`](prompt-architect/README.md).
- **Tham chiếu đầy đủ:** [`GUIDE-COMPLETE.md`](GUIDE-COMPLETE.md).

---

## Hỏi đáp nhanh

**Q. Tại sao scaffold trắng lại fail cổng permission?**

Vì cổng không phải là check cú pháp. Nó yêu cầu bằng chứng thật (walk-forward,
Monte Carlo, multi-broker, strategy có chạy) trước khi cho EA deploy. Một
template mới phải fail — nếu nó pass, cổng chính là theatre.

**Q. Ma trận 8×8 hiện 56/64 PASS mà tôi chưa làm gì?**

Số đó là **maximum cấu trúc, không phải số đo**. `mql5-rri-bt` mặc định mark
mọi cell ngoài trục `live-canary` là PASS trừ khi bạn truyền report backtest
chứa từ `fail`. Ma trận hữu dụng như danh sách chiều cần phủ, không phải điểm.

**Q. Tôi disable được 1 anti-pattern cho 1 file không?**

Hiện tại không. Không có directive kiểu `// vibekit-disable AP-05` — chủ ý
để contract của cổng minh bạch. Nếu rule sai với use case của bạn, sửa trực
tiếp `scripts/vibecodekit_mql5/lint.py` và gửi PR.

**Q. Có 46 CLI quá nhiều. Tôi nên bắt đầu với cái nào?**

Năm CLI dùng hằng ngày: `mql5-build`, `mql5-lint`, `mql5-trader-check`,
`mql5-permission`, `mql5-compile`. Còn lại là auxiliary, bỏ qua tới khi cần.

**Q. Kit này đã production-ready cho live trading chưa?**

Các thư viện (`CPipNormalizer`, `CRiskGuard`, `CMagicRegistry`) là hygiene
production-grade. Strategy là cái bạn viết trong `OnTick` — kit không claim
gì về tính sinh lời. Luôn demo trước.
