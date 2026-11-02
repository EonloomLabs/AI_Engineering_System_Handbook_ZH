# Kỹ thuật hệ thống AI: từ cơ sở đến bên trong

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md) · [Español](README.es.md) · **Tiếng Việt**

Giáo trình ngoại tuyến · khái niệm cơ sở, cơ chế bên trong, thực hành kỹ thuật

Từ cơ sở đến bên trong: hiểu cách mô hình ngôn ngữ lớn xử lý đầu vào và sinh đầu ra, nắm cách Agent sử dụng công cụ, quản lý ngữ cảnh và bộ nhớ, đồng thời cải thiện chất lượng kỹ thuật bằng phương pháp có thể kiểm chứng.

## Mở sách

Giải nén rồi mở [`vi/index.html`](vi/index.html). Không cần máy chủ, không cần mạng, không cần API mô hình hay khóa.
Nút chuyển ngôn ngữ ở đầu mỗi trang dẫn đến đúng trang đó trong bản ngôn ngữ khác.

## Cấu trúc khóa học

Mạch chính gồm năm giai đoạn và 68 bài: quan sát hệ thống trước, rồi lần theo từng lớp vào bên trong mô hình, cuối cùng trở lại phần kiểm chứng toàn bộ hệ thống.

| Giai đoạn | Bài | Nội dung |
| --- | --- | --- |
| Quan sát hệ thống | 01—06 | Biến một lần chạy tác vụ thành bằng chứng kiểm tra được, trước khi bàn đến thay đổi |
| Xây dựng vòng lặp | 07—28 | Gọi công cụ, ngữ cảnh, truy hồi, bộ nhớ và phục hồi sau lỗi |
| Tối ưu hộp đen | 29—34 | Chưa mở mô hình: dùng quyền hạn, tác vụ cố định và phép đo thời gian đầy đủ để xét tối ưu có hiệu quả hay không |
| Tiếp quản mô hình | 35—63 | Từ giao diện dịch vụ đi vào tensor, lượt truyền thuận, huấn luyện, suy luận, đến GPU và điều phối |
| Kiểm chứng toàn bộ hệ thống | 64—68 | Nối đa phương thức, độ bất định và tối ưu xuyên lớp về cùng một bộ tiêu chí nghiệm thu |

40 bài phần cơ sở có câu tự kiểm; 28 chương phần hệ thống triển khai quanh 112 câu hỏi chính. Mười hai chủ đề đọc cho phép vào từ một vấn đề cụ thể khi đã có nền tảng.
Chính văn, hình giải thích và phần giải nghĩa công thức đều mở sẵn; đáp án tự kiểm mặc định thu gọn.

## Vị trí các phần

| Đường dẫn | Nội dung |
| --- | --- |
| [`vi/index.html`](vi/index.html) | Điểm vào đọc sách |
| [`vi/complete.html`](vi/complete.html) | Cùng nội dung ở dạng đọc liên tục, không phụ thuộc tệp khác |
| [`vi/worked-examples.html`](vi/worked-examples.html) | Mục lục ví dụ đã giải, tra theo số hiệu |
| [`vi/worked-model.html`](vi/worked-model.html) | Cùng hai câu đó, tính trọn mọi ma trận trung gian |
| [`labs/model/`](labs/model/) | Mã ví dụ mô hình, tham số gốc, tham số sau huấn luyện và bản ghi số |
| [`worked-examples/`](worked-examples/) | Chứng cứ số và trạng thái tất định, chạy được |
| [`diagrams/`](diagrams/) | Mã nguồn hình, dữ liệu và kiểm tra |
| [`wiki/`](wiki/) | Chính văn và mục lục wiki có thể chỉnh sửa |
| [`editorial/`](editorial/) | Phương pháp biên soạn và bản ghi chuyển nội dung |
| [`validation/integration/`](validation/integration/) | Kiểm tra của vòng này |
| [`i18n/`](i18n/) | Bảng dịch đa ngữ, công cụ và bản ghi xác minh |

## Tính lại các con số

Không cần mạng, GPU hay khóa API. Với Python 3.10 trở lên, chạy trong thư mục đã giải nén:

```bash
python3 worked-examples/run_all.py
```

Mã chạy được và dữ liệu mô hình nằm ở thư mục gốc, dùng chung cho mọi bản ngôn ngữ; chú thích và đầu ra của script bằng tiếng Trung.
Đổi một ví dụ thì phải chạy lại, đồng thời cập nhật hình, chữ, chỉ mục tìm kiếm và bản liên tục — quy ước nằm trong [`AGENTS.md`](AGENTS.md).

## Các bản ngôn ngữ

| Ngôn ngữ | Điểm vào |
| --- | --- |
| 简体中文 (bản gốc đối chiếu) | [`index.html`](index.html) |
| English | [`en/index.html`](en/index.html) |
| 日本語 | [`ja/index.html`](ja/index.html) |
| Español | [`es/index.html`](es/index.html) |
| Tiếng Việt | [`vi/index.html`](vi/index.html) |

Mỗi bản gồm 262 trang phân trang cùng một `complete.html` chứa đúng nội dung đó. Tiếng Trung là bản gốc đối chiếu; thắc mắc về bản dịch và chỗ nghi vấn trong nguyên văn được ghi vào [`i18n/SOURCE-ISSUES.md`](i18n/SOURCE-ISSUES.md) chứ không tự ý sửa.

## Giới hạn xác thực

401 ví dụ giảng dạy không tương đương 401 thí nghiệm về năng lực mô hình. Các kiểm thử đối chiếu công thức số học, chiều, tính nhân quả, gradient, phân mảnh giao thức và hành vi trạng thái đã đơn giản hóa; những ví dụ tình huống khác suy luận tường minh từ tiền đề đã nêu.
Chúng không chứng minh hiệu quả của Agent thương mại, tốc độ GPU, phần bên trong của mã nguồn đóng hay mức an toàn khi vận hành thật.
Nguồn trỏ tới tệp, hàm và số dòng thực tế; suy dẫn kỹ thuật, đo thực tế và mô phỏng giảng dạy được ghi rõ tách biệt.
Việc làm tròn trong hình số chỉ phục vụ hiển thị; phép tính dùng độ chính xác gốc.

Phạm vi xác minh nguồn xem tại [`engineering/agent-evidence.html`](engineering/agent-evidence.html), bản ghi máy nằm ở `engineering/agent-practice/verified/`.
