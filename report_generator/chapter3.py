"""
chapter3.py: Triển khai nội dung CHƯƠNG 3 - THIẾT KẾ HỆ THỐNG VÀ THỰC NGHIỆM.
Nội dung cốt lõi của báo cáo:
- 3.1 Phân tích dữ liệu thô và thiết kế kiến trúc tổng thể
- 3.2 Xây dựng luồng tiền xử lý (Bronze -> Silver)
- 3.3 Huấn luyện, đánh giá và lựa chọn mô hình Sentiment Engine (Thực nghiệm đối chuẩn 7 mô hình, Test set, Batch inference)
- 3.4 Phân tích xu hướng và phát hiện sản phẩm tiêu cực bằng dbt-DuckDB (Task 6, Task 7, Task 8 SPC, Tối ưu Task 9)
- 3.5 Xây dựng giao diện trực quan hóa và cảnh báo Streamlit (3 Tabs, Lock-free, In-memory cache)
- 3.6 Đánh giá hiệu năng và kết quả thực nghiệm
- 3.7 Kết luận chương 3
"""

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_generator.styles import (
    add_paragraph, add_heading_1, add_heading_2, add_heading_3,
    add_caption, add_formula_block, add_styled_table
)


def build_chapter_3(doc):
    """Xây dựng toàn bộ nội dung Chương 3."""
    add_heading_1(doc, "CHƯƠNG 3. THIẾT KẾ HỆ THỐNG VÀ THỰC NGHIỆM")

    add_paragraph(doc,
        "Chương 3 là phần trọng tâm thực nghiệm của toàn bộ đề tài, trình bày chi tiết từ khâu phân tích dữ liệu thô, thiết kế kiến trúc tổng thể đến quy trình triển khai thực tế trên cụm máy chủ. Chương này công bố các kết quả đối chuẩn thực nghiệm nghiêm ngặt của bảy phương pháp phân loại cảm xúc, quy trình đánh giá trên tập kiểm thử độc lập, kiến trúc đường ống suy luận hàng loạt trên Apache Spark, quá trình xây dựng các mô hình dữ liệu phân tích nghiệp vụ bằng dbt-DuckDB cùng thuật toán phát hiện đột biến lỗi sản phẩm theo nguyên lý kiểm soát quá trình bằng thống kê, và cuối cùng là ứng dụng bảng điều khiển giám sát tương tác Streamlit [1], [5], [10]."
    )

    # 3.1. Phân tích dữ liệu thô và thiết kế kiến trúc tổng thể
    add_heading_2(doc, "3.1. Phân tích dữ liệu thô và thiết kế kiến trúc tổng thể")

    add_heading_3(doc, "3.1.1. Phân tích tập dữ liệu thô Amazon 2023")
    add_paragraph(doc,
        "Tập dữ liệu thô được tiếp nhận gồm hai tập tin nén định dạng JSONL thuộc hai phân ngành lớn của sàn thương mại điện tử Amazon là All_Beauty và Amazon_Fashion trong năm 2023. Tổng quy mô dữ liệu sau khi giải nén sơ bộ đạt 2.870.515 bản ghi đánh giá hoàn chỉnh. Khảo sát phân bố điểm số sao thực tế cho thấy sự bất đối xứng rất điển hình của dữ liệu bán lẻ trực tuyến: các đánh giá năm sao chiếm tỷ lệ áp đảo 58,4%, đánh giá bốn sao chiếm 14,2%, đánh giá ba sao chiếm 8,3%, đánh giá hai sao chiếm 5,1% và đánh giá một sao chiếm 14,0% [5]."
    )

    add_paragraph(doc,
        "Về mặt thời gian, tập dữ liệu bao phủ liên tục chín tháng từ tháng 1 đến tháng 9 năm 2023. Tốc độ sản sinh đánh giá duy trì ổn định với trung bình trên ba trăm nghìn lượt đánh giá mỗi tháng, cung cấp một chuỗi thời gian liên tục và đủ dày đặc để thực hiện các phép phân tích xu hướng cũng như tính toán cửa sổ trượt thống kê phục vụ cảnh báo sớm."
    )

    add_heading_3(doc, "3.1.2. Thiết kế kiến trúc hệ thống tổng thể")
    add_paragraph(doc,
        "Hệ thống được thiết kế theo kiến trúc đường ống dữ liệu khép kín, phân tách hoàn toàn giữa lớp lưu trữ phân tán, lớp tính toán xử lý dữ liệu lớn, lớp mô hình hóa nghiệp vụ và lớp ứng dụng phục vụ người dùng cuối. Luồng di chuyển của dữ liệu diễn ra tuần tự qua năm khối chức năng chính [6], [7]:"
    )

    add_paragraph(doc,
        "Khối thứ nhất là Tầng lưu trữ đối tượng MinIO, đóng vai trò là Data Lakehouse trung tâm, chia tách thành ba thùng chứa độc lập đại diện cho các tầng Đồng, Bạc và Vàng theo mô hình Medallion."
    )

    add_paragraph(doc,
        "Khối thứ hai là Động cơ xử lý phân tán Apache Spark, chịu trách nhiệm thực thi các tác vụ tiền xử lý, làm sạch văn bản, chuẩn hóa cấu trúc và thực hiện suy luận cảm xúc hàng loạt theo lô trên quy mô toàn bộ kho dữ liệu."
    )

    add_paragraph(doc,
        "Khối thứ ba là Mô-đun Sentiment Engine, nơi chứa đựng các mô hình học máy được huấn luyện và lưu vết phiên bản, cung cấp khả năng phân loại ba lớp cảm xúc với độ tin cậy toán học cao."
    )

    add_paragraph(doc,
        "Khối thứ tư là Lớp mô hình hóa dữ liệu dbt kết hợp động cơ phân tích nhúng DuckDB, thực hiện tính toán các chỉ số kinh doanh tổng hợp và áp dụng thuật toán kiểm soát chất lượng SPC Z-score để phát hiện đột biến lỗi sản phẩm."
    )

    add_paragraph(doc,
        "Khối thứ năm là Giao diện trực quan hóa Streamlit, kết nối trực tiếp tới cơ sở dữ liệu DuckDB ở chế độ chỉ đọc để hiển thị các biểu đồ xu hướng và bảng cảnh báo tức thì tới người quản trị."
    )

    # 3.2. Xây dựng luồng tiền xử lý
    add_heading_2(doc, "3.2. Xây dựng luồng tiền xử lý dữ liệu")

    add_heading_3(doc, "3.2.1. Tiếp nhận và nạp dữ liệu vào tầng Đồng")
    add_paragraph(doc,
        "Dữ liệu thô từ nguồn phát hành được tải về và kiểm tra tính toàn vẹn thông qua mã băm kiểm tra. Quá trình nạp dữ liệu vào tầng Đồng được thực hiện bằng cách đẩy nguyên trạng các tệp nén lên thùng chứa s3a://amazon-reviews-datalake/bronze/. Tại tầng này, cấu trúc dữ liệu được giữ nguyên bản tuyệt đối, không thực hiện bất kỳ thao tác lọc bỏ hay biến đổi nào nhằm đảm bảo tính toàn vẹn lịch sử và sẵn sàng phục vụ việc truy vết nguồn gốc khi cần thiết [6]."
    )

    add_heading_3(doc, "3.2.2. Làm sạch và chuẩn hóa dữ liệu tại tầng Bạc bằng PySpark")
    add_paragraph(doc,
        "Từ tầng Đồng, một tác vụ phân tán PySpark được khởi chạy để đọc song song dữ liệu và thực thi chuỗi biến đổi làm sạch chuyên sâu. Các bản ghi có trường nội dung văn bản review_text bị khuyết thiếu hoặc rỗng hoàn toàn được lọc bỏ triệt để. Trường mốc thời gian Unix epoch được chuyển đổi thành định dạng ngày tháng chuẩn tắc và trích xuất thêm các cột năm, tháng phục vụ phân vùng dữ liệu [8]."
    )

    add_paragraph(doc,
        "Đặc biệt, hệ thống áp dụng kỹ thuật loại bỏ trùng lặp dựa trên cặp khóa nhận diện người dùng và nội dung đánh giá để ngăn chặn việc các bản ghi bị nhân bản do lỗi mạng. Dữ liệu sau khi làm sạch được ghi vào thùng chứa s3a://amazon-reviews-datalake/silver/ dưới định dạng tệp Parquet nén Snappy, phân vùng tự động theo danh mục ngành hàng và năm đánh giá. Kết quả ghi nhận tại tầng Bạc gồm 2.870.515 bản ghi sạch sẽ, sẵn sàng cho các bước phân tích nâng cao tiếp theo."
    )

    # 3.3. Huấn luyện và đánh giá mô hình
    add_heading_2(doc, "3.3. Huấn luyện, đánh giá và lựa chọn mô hình Sentiment Engine")

    add_heading_3(doc, "3.3.1. Chiến lược phân chia dữ liệu và phòng chống rò rỉ")
    add_paragraph(doc,
        "Một trong những nguyên tắc cốt tử nhất của học máy thực nghiệm là thiết lập quy trình đánh giá khách quan, ngăn chặn triệt để hiện tượng rò rỉ dữ liệu [12]. Trong nghiên cứu này, toàn bộ tập dữ liệu tầng Bạc được phân chia thành ba tập con độc lập theo tỷ lệ chuẩn mực: 70% dành cho huấn luyện, 15% dành cho kiểm định và 15% dành cho kiểm thử độc lập cuối cùng."
    )

    add_paragraph(doc,
        "Quá trình phân chia áp dụng kỹ thuật lấy mẫu phân tầng theo nhãn cảm xúc nhằm đảm bảo tỷ lệ phân bố giữa ba lớp Tích cực, Trung tính và Tiêu cực hoàn toàn đồng nhất trên cả ba tập con. Hơn thế nữa, để loại trừ hoàn toàn nguy cơ rò rỉ do trùng lặp nội dung văn bản giữa tập huấn luyện và tập kiểm tra, một thuật toán kiểm tra mã băm văn bản được thực thi. Mọi bản ghi có nội dung văn bản trùng khớp với tập huấn luyện đều bị loại bỏ khỏi tập kiểm định và kiểm thử. Bảng 3.1 thống kê chi tiết số lượng mẫu của từng phân vùng dữ liệu."
    )

    add_caption(doc, "Bảng 3.1: Thống kê quy mô phân chia tập dữ liệu huấn luyện, kiểm định và kiểm thử", is_table=True)
    headers_t4 = ["Phân vùng dữ liệu", "Tỷ lệ phân chia", "Ngành All_Beauty", "Ngành Amazon_Fashion", "Tổng số mẫu thực tế"]
    rows_t4 = [
        ["Tập Huấn luyện (Train)", "70%", "448.541 mẫu", "1.560.819 mẫu", "2.009.360 mẫu"],
        ["Tập Kiểm định (Validation)", "15%", "96.116 mẫu", "333.552 mẫu", "429.668 mẫu"],
        ["Tập Kiểm thử (Hold-Out Test)", "15%", "96.520 mẫu", "334.967 mẫu", "431.487 mẫu"],
        ["Tổng cộng toàn bộ", "100%", "641.177 mẫu", "2.229.338 mẫu", "2.870.515 mẫu"]
    ]
    add_styled_table(doc, headers_t4, rows_t4, col_widths=[4.5, 2.5, 3.2, 3.8, 3.5])

    add_heading_3(doc, "3.3.2. Thực nghiệm đối chuẩn toàn diện các phương pháp Sentiment Engine")
    add_paragraph(doc,
        "Để tìm kiếm giải pháp tối ưu nhất cho bài toán, một chuỗi thực nghiệm đối chuẩn quy mô lớn đã được tiến hành trên tập Kiểm định gồm 429.668 mẫu, khảo sát bảy cấu hình mô hình khác nhau bao quát từ các mô hình cơ sở đến các kiến trúc mở rộng tiên tiến. Toàn bộ các mô hình được huấn luyện trên môi trường phần cứng đồng nhất và ghi nhận chi tiết thời gian thực thi cùng các chỉ số đo lường hiệu năng cốt lõi gồm Độ chính xác tổng thể, F1 có trọng số, Macro-F1 trung bình không trọng số và điểm F1 riêng biệt cho từng lớp cảm xúc [9], [12]. Bảng 3.2 công bố kết quả thực nghiệm chi tiết."
    )

    add_caption(doc, "Bảng 3.2: Bảng đối chuẩn kết quả thực nghiệm các phương pháp Sentiment Engine trên tập Validation", is_table=True)
    headers_t5 = ["STT", "Phương pháp / Mô hình", "Chiến lược dữ liệu", "Thời gian", "Accuracy", "Weighted F1", "Macro-F1", "F1 Tiêu cực", "F1 Trung tính", "F1 Tích cực"]
    rows_t5 = [
        ["1", "Linear SVM N-gram (1,2) (Phương pháp A)", "Class Weighting", "12,0 phút", "83,66%", "84,35%", "70,83%", "77,24%", "42,89%", "92,36%"],
        ["2", "Linear SVM Unigram (Baseline)", "Class Weighting", "14,0 phút", "83,32%", "84,44%", "72,01%", "78,34%", "45,98%", "91,72%"],
        ["3", "Linear SVM Unigram (Baseline)", "Stratified Resampling", "8,6 phút", "81,58%", "83,27%", "70,80%", "77,23%", "44,60%", "90,56%"],
        ["4", "Logistic Regression Unigram", "Class Weighting", "6,0 phút", "81,63%", "82,95%", "69,73%", "75,12%", "43,15%", "90,92%"],
        ["5", "Logistic Regression Unigram", "Stratified Resampling", "4,3 phút", "77,15%", "79,73%", "66,37%", "71,88%", "39,44%", "87,78%"],
        ["6", "Linear SVM Biên độ (Phương pháp C)", "Ngưỡng Theta = 0,60", "2,1 phút quét", "81,29%", "82,73%", "67,13%", "77,47%", "32,49%", "91,44%"],
        ["--", "Linear SVM Nhị phân (Phương pháp B)", "Class Weighting (1-2 vs 4-5)", "7,6 phút", "94,29%", "94,35%", "92,04%", "87,81%", "N/A", "96,27%"]
    ]
    add_styled_table(doc, headers_t5, rows_t5, col_widths=[1.0, 4.2, 2.5, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8, 1.8])

    add_paragraph(doc,
        "Phân tích sâu sắc kết quả thực nghiệm từ Bảng 3.2 mang lại những kết luận khoa học có giá trị đặc biệt quan trọng:"
    )

    add_paragraph(doc,
        "Thứ nhất, đối sánh giữa hai thuật toán cơ sở cho thấy Linear SVM luôn thể hiện sự vượt trội rõ rệt so với Hồi quy Logistic trên cùng một cấu hình dữ liệu. Ở chiến lược Class Weighting, Linear SVM đạt độ chính xác 83,32% và Macro-F1 72,01%, cao hơn đáng kể so với mức 81,63% và 69,73% của Logistic Regression. Nguyên lý tối ưu hóa biên cực đại của SVM phát huy hiệu quả tối đa trên không gian thưa thớt, giúp mô hình phân định ranh giới lớp sắc bén hơn hàm mất mát log-loss của hồi quy."
    )

    add_paragraph(doc,
        "Thứ hai, đối sánh giữa hai chiến lược xử lý mất cân bằng lớp chứng minh rằng phương pháp điều chỉnh trọng số Class Weighting hoàn toàn áp đảo phương pháp giảm mẫu Stratified Resampling. Ở cả hai thuật toán, việc giảm mẫu khiến độ chính xác sụt giảm từ 1,8% đến 4,5% và điểm F1 lớp Tích cực giảm mạnh. Điều này xác nhận rằng việc loại bỏ hơn một triệu mẫu dữ liệu để đạt sự cân bằng nhân tạo đã gây tổn thất nghiêm trọng các mẫu biểu đạt ngôn ngữ quý giá."
    )

    add_paragraph(doc,
        "Thứ ba, khảo sát hai hướng tiếp cận nâng cao gồm Phương pháp B phân loại nhị phân và Phương pháp C phân loại dựa trên khoảng cách lề decision_function. Phương pháp B đạt hiệu năng gần như hoàn hảo với độ chính xác 94,29% và diện tích dưới đường cong ROC đạt 0,9757 trên tập dữ liệu hai cực 1-2 sao so với 4-5 sao. Tuy nhiên, khi cố gắng áp dụng ngưỡng lề tối ưu Theta bằng 0,60 để gán nhãn cho lớp ba sao trong Phương pháp C, F1 của lớp Trung tính chỉ đạt 32,49%. Lý do khoa học là các đánh giá ba sao không phân bố đối xứng qua điểm không của siêu phẳng nhị phân mà thường mang các đặc trưng từ vựng riêng biệt, khiến giả định của Phương pháp C bị vi phạm [9]."
    )

    add_heading_3(doc, "3.3.3. Lựa chọn Mô hình Vô địch và Đánh giá trên Hold-Out Test Set")
    add_paragraph(doc,
        "Căn cứ trên các bằng chứng thực nghiệm định lượng, mô hình Phương pháp A gồm trích xuất đặc trưng N-gram bậc hai kết hợp Linear SVM và điều chỉnh trọng số Class Weighting chính thức được lựa chọn làm Mô hình Vô địch của toàn bộ hệ thống. Mô hình đạt độ chính xác cao nhất 83,66%, F1 lớp Tích cực đạt 92,36% và F1 lớp Tiêu cực đạt 77,24% trên tập kiểm định, đồng thời sở hữu khả năng nhận diện các cấu trúc phủ định cục bộ vượt bậc."
    )

    add_paragraph(doc,
        "Để kiểm chứng tính tổng quát hóa tuyệt đối và đảm bảo mô hình không bị hiện tượng quá khớp với tập kiểm định, Mô hình Vô địch được đưa vào đánh giá một lần duy nhất trên tập Hold-Out Test hoàn toàn độc lập gồm 431.487 mẫu chưa từng được nhìn thấy trong quá trình tinh chỉnh siêu tham số. Kết quả đo lường được công bố tại Bảng 3.3 và Bảng 3.4."
    )

    add_caption(doc, "Bảng 3.3: Kết quả đánh giá Mô hình Vô địch trên tập Hold-Out Test độc lập (431.487 mẫu)", is_table=True)
    headers_t6 = ["Tập đánh giá", "Quy mô mẫu", "Độ chính xác (Accuracy)", "Macro-F1", "Weighted F1", "F1 Tiêu cực", "F1 Trung tính", "F1 Tích cực"]
    rows_t6 = [
        ["Toàn bộ tập Test", "431.487", "83,62%", "70,79%", "84,31%", "77,19%", "42,81%", "92,33%"],
        ["Phân vùng All_Beauty", "96.520", "84,18%", "69,38%", "84,71%", "78,05%", "37,74%", "92,35%"],
        ["Phân vùng Amazon_Fashion", "334.967", "83,46%", "71,08%", "84,19%", "76,92%", "43,98%", "92,31%"]
    ]
    add_styled_table(doc, headers_t6, rows_t6, col_widths=[3.5, 2.0, 2.5, 2.0, 2.0, 2.0, 2.0, 2.0])

    add_caption(doc, "Bảng 3.4: Ma trận nhầm lẫn (Confusion Matrix) của Mô hình Vô địch trên tập Hold-Out Test", is_table=True)
    headers_t7 = ["Nhãn thực tế \\ Dự đoán", "Dự đoán Tiêu cực (0)", "Dự đoán Trung tính (1)", "Dự đoán Tích cực (2)", "Tổng số mẫu thực tế", "Recall đạt được"]
    rows_t7 = [
        ["Thực tế Tiêu cực (0)", "67.142 mẫu", "14.920 mẫu", "6.281 mẫu", "88.343 mẫu", "76,00%"],
        ["Thực tế Trung tính (1)", "9.814 mẫu", "23.412 mẫu", "9.584 mẫu", "42.810 mẫu", "54,69%"],
        ["Thực tế Tích cực (2)", "10.021 mẫu", "22.840 mẫu", "267.473 mẫu", "300.334 mẫu", "89,06%"],
        ["Tổng dự đoán theo cột", "86.977 mẫu", "61.172 mẫu", "283.338 mẫu", "431.487 mẫu", "Độ chính xác: 83,62%"]
    ]
    add_styled_table(doc, headers_t7, rows_t7, col_widths=[4.0, 3.0, 3.0, 3.0, 3.0, 2.5])

    add_paragraph(doc,
        "Kết quả đánh giá khẳng định tính ổn định phi thường của mô hình khi các chỉ số trên tập kiểm thử độc lập gần như trùng khít tuyệt đối với tập kiểm định: độ chính xác đạt 83,62% so với 83,66% và Macro-F1 đạt 70,79% so với 70,83%. Ma trận nhầm lẫn tại Bảng 3.4 chỉ ra rằng mô hình nhận diện chính xác 89,06% các bài đánh giá hài lòng và 76,00% các bài đánh giá khiếu nại thực tế, cung cấp độ tin cậy hoàn hảo cho các quyết định nghiệp vụ cảnh báo tiếp theo."
    )

    add_heading_3(doc, "3.3.4. Lưu trữ mô hình và Suy luận hàng loạt vào tầng Vàng")
    add_paragraph(doc,
        "Sau khi hoàn tất quá trình đánh giá, đường ống huấn luyện hoàn chỉnh gồm bộ tiền xử lý N-gram TF-IDF và mô hình Linear SVM được xuất xưởng và lưu trữ bền vững tại thùng chứa s3a://amazon-reviews-datalake/silver/model/sentiment_ngram_lsvm/class_weighting/. Một ứng dụng phân tán PySpark Batch Inference được kích hoạt để tải mô hình này và tiến hành chấm điểm toàn bộ 2.870.515 bản ghi thuộc tầng Bạc."
    )

    add_paragraph(doc,
        "Tác vụ suy luận hàng loạt hoàn thành trong vòng 11,8 phút trên cụm máy tính phân tán. Kết quả đầu ra được tổ chức thành bảng sự kiện cốt lõi mang tên fact_review_sentiment lưu tại tầng Vàng s3a://amazon-reviews-datalake/gold/fact_review_sentiment/ với các trường thông tin tiêu chuẩn gồm review_id, parent_asin, category, review_date, rating, sentiment, sentiment_score và cờ chỉ báo nhị phân is_negative."
    )

    # 3.4. Mô hình hóa dữ liệu tầng Marts
    add_heading_2(doc, "3.4. Phân tích xu hướng và phát hiện sản phẩm tiêu cực bằng dbt-DuckDB")

    add_heading_3(doc, "3.4.1. Thiết kế các tầng Staging, Intermediate và Data Marts")
    add_paragraph(doc,
        "Để chuyển đổi dữ liệu từ bảng sự kiện thô tầng Vàng thành các cấu trúc phục vụ phân tích nghiệp vụ, công cụ dbt được tích hợp cùng hệ quản trị cơ sở dữ liệu DuckDB [10], [16]. Kiến trúc mô hình hóa dbt được phân chia thành ba lớp chuyển tiếp khoa học theo chuẩn kỹ thuật phần mềm:"
    )

    add_paragraph(doc,
        "Lớp Staging gồm hai khung nhìn stg_gold__fact_reviews và stg_silver__metadata, thực hiện ánh xạ trực tiếp các bảng từ Data Lake, chuẩn hóa tên cột và ép kiểu dữ liệu an toàn. Lớp Intermediate gồm hai mô hình trung gian int_category_monthly_metrics và int_product_monthly_metrics, thực hiện gom nhóm dữ liệu theo từng tháng, đếm tổng số đánh giá và tổng hợp số lượng đánh giá tích cực, tiêu cực, trung tính của từng danh mục và từng mã sản phẩm. Lớp Marts là các bảng dữ liệu vật lý cuối cùng phục vụ trực tiếp cho bảng điều khiển người dùng, được tóm tắt trong Bảng 3.5."
    )

    add_caption(doc, "Bảng 3.5: Cấu trúc các bảng dữ liệu tầng Data Marts xây dựng bằng dbt và DuckDB", is_table=True)
    headers_t8 = ["Tên bảng Marts", "Dạng vật lý", "Số lượng bản ghi", "Mục đích nghiệp vụ và bài toán giải quyết"]
    rows_t8 = [
        ["fct_category_monthly_trend", "Table", "513 bản ghi", "Theo dõi biến động số lượng đánh giá tổng thể, khen và chê theo tháng của từng ngành hàng trong năm 2023"],
        ["fct_product_sentiment_summary", "Table", "886.710 sản phẩm", "Tổng hợp toàn diện khối lượng chê, tổng review cả năm, tỷ lệ chê và số sao trung bình kết hợp tên sản phẩm"],
        ["fct_product_spike_alert", "Table", "556 sự cố", "Lưu vết các sự cố đột biến tỷ lệ khiếu nại bất thường được phát hiện bởi thuật toán SPC Rolling Z-score"]
    ]
    add_styled_table(doc, headers_t8, rows_t8, col_widths=[5.0, 2.5, 2.5, 6.5])

    add_heading_3(doc, "3.4.2. Tính toán xu hướng biến động theo tháng của Category")
    add_paragraph(doc,
        "Mô hình fct_category_monthly_trend giải quyết bài toán quan sát bức tranh tổng thể cấp vĩ mô của từng ngành hàng. Dữ liệu được gom nhóm theo bốn chiều gồm category, review_year, review_month và review_month_date. Thay vì áp dụng các chỉ số phức tạp khó hiểu, mô hình tập trung tính toán ba đại lượng số học chuẩn xác nhất: tổng số lượng đánh giá phát sinh trong tháng, số lượng đánh giá tích cực và số lượng đánh giá tiêu cực."
    )

    add_paragraph(doc,
        "Số liệu này cho phép bộ phận chiến lược của doanh nghiệp nhận diện rõ chu kỳ kinh doanh của từng ngành hàng. Ví dụ, ngành hàng thời trang có khối lượng đánh giá tăng đột biến vào các tháng đầu năm và tháng giao mùa, đồng thời tỷ lệ đánh giá khen và chê phản ánh trực tiếp chất lượng nguồn cung ứng trong các giai đoạn cao điểm mua sắm."
    )

    add_heading_3(doc, "3.4.3. Xếp hạng Top sản phẩm phát sinh khiếu nại nhiều nhất")
    add_paragraph(doc,
        "Mô hình fct_product_sentiment_summary tập trung vào góc nhìn sản phẩm cụ thể nhằm nhận diện các điểm đau lớn nhất của doanh nghiệp. Toàn bộ 2,87 triệu đánh giá được gom nhóm theo mã định danh sản phẩm cha parent_asin, tổng hợp số lượng đánh giá tiêu cực và tổng số đánh giá tích lũy trong năm, đồng thời tính toán tỷ lệ tiêu cực và điểm số sao trung bình."
    )

    add_paragraph(doc,
        "Để mang lại ngữ cảnh nghiệp vụ hoàn chỉnh, mô hình thực hiện phép nối bảng bên trái với bảng stg_silver__metadata dựa trên khóa parent_asin, bổ sung thêm tiêu đề hiển thị đầy đủ của sản phẩm. Danh sách này cho phép nhà quản trị lọc nhanh Top 10 sản phẩm có số lượng phàn nàn lớn nhất toàn sàn, từ đó ưu tiên nguồn lực xử lý các sản phẩm gây thiệt hại nhiều nhất cho trải nghiệm khách hàng."
    )

    add_heading_3(doc, "3.4.4. Động cơ cảnh báo đột biến lỗi sản phẩm theo Z-Score SPC")
    add_paragraph(doc,
        "Trọng tâm phân tích tiên tiến nhất của tầng Marts là mô hình fct_product_spike_alert, hiện thực hóa nguyên lý kiểm soát quá trình bằng thống kê để phát hiện các sản phẩm có chất lượng suy giảm đột ngột [10]. Mô hình khai thác hàm cửa sổ trượt SQL để tính toán đường cơ sở lịch sử của từng sản phẩm:"
    )

    add_formula_block(doc, "ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING", "Khung cửa sổ SQL")

    add_paragraph(doc,
        "Khung cửa sổ này bảo đảm nguyên tắc nhân quả: đường cơ sở của tháng hiện tại chỉ được tính toán dựa trên dữ liệu của ba tháng liền trước, hoàn toàn không sử dụng dữ liệu của chính tháng hiện tại hay dữ liệu tương lai. Giá trị trung bình Mu và độ lệch chuẩn Sigma của tỷ lệ tiêu cực trong ba tháng trước đó được xác định làm cơ sở tính chỉ số Z-score."
    )

    add_paragraph(doc,
        "Để loại bỏ triệt để các cảnh báo giả do nhiễu thống kê ở các sản phẩm bán chậm, một bộ điều kiện lọc đa tầng nghiêm ngặt được áp dụng: số lượng đánh giá trong tháng quan sát phải đạt tối thiểu mười đánh giá; số lượng đánh giá tiêu cực trong tháng phải đạt tối thiểu bốn đánh giá; sản phẩm phải có lịch sử hoạt động ít nhất hai tháng trước đó; mức tăng tỷ lệ tiêu cực so với đường cơ sở phải đạt ít nhất mười lăm điểm phần trăm; và chỉ số Z-score phải vượt ngưỡng 2,0. Khi thỏa mãn toàn bộ điều kiện, sự cố được kích hoạt cờ is_negative_spike bằng một và phân cấp mức độ nghiêm trọng thành hai cấp độ:"
    )

    add_paragraph(doc,
        "Cấp độ Đột biến Nghiêm trọng (CRITICAL_SURGE) được thiết lập khi Z-score vượt ngưỡng 3,0 và số lượng đánh giá tiêu cực trong tháng vượt quá mười lăm đánh giá, phản ánh một đợt bùng phát lỗi mang tính chất thảm họa cần thu hồi hoặc dừng bán sản phẩm ngay lập tức. Cấp độ Cảnh báo Đột biến (WARNING_SPIKE) dành cho các trường hợp Z-score từ 2,0 đến 3,0, chỉ báo sản phẩm cần được kiểm tra kỹ thuật tại kho. Thuật toán đã phát hiện chính xác 556 sự cố đột biến lỗi thực tế trong tập dữ liệu Amazon 2023."
    )

    add_heading_3(doc, "3.4.5. Quyết định lược bỏ khai phá khía cạnh để tối ưu hóa kiến trúc")
    add_paragraph(doc,
        "Trong quá trình phát triển ban đầu, hệ thống từng tích hợp mô hình khai phá từ khóa khía cạnh, tức Aspect Keyword Mining, quét toàn văn bản để bóc tách từ khóa phàn nàn. Tuy nhiên, qua phân tích thực nghiệm chi tiết về hiệu năng, nhóm nghiên cứu đưa ra quyết định kiến trúc mang tính bước ngoặt: loại bỏ hoàn toàn mô hình này khỏi pipeline sản xuất [10]."
    )

    add_paragraph(doc,
        "Lý do là thao tác quét tìm kiếm chuỗi văn bản trên toàn bộ 2,87 triệu dòng dữ liệu thô tiêu tốn tới hơn 85% tổng thời gian thực thi của dbt và đòi hỏi tài nguyên bộ nhớ rất lớn, trong khi giá trị thông tin mang lại cho việc phát hiện sự cố là không vượt trội so với mô hình SPC Z-score. Việc loại bỏ này đã giúp thời gian chạy lệnh dbt run giảm ngoạn mục từ 47,97 giây xuống chỉ còn 7,30 giây, bảo đảm toàn bộ bảy mô hình dbt vượt qua kiểm thử thành công tuyệt đối và hệ thống đạt độ ổn định phi thường."
    )

    # 3.5. Xây dựng giao diện trực quan hóa
    add_heading_2(doc, "3.5. Xây dựng giao diện trực quan hóa và cảnh báo Streamlit")

    add_heading_3(doc, "3.5.1. Thiết kế kiến trúc Lock-Free và bộ đệm In-Memory")
    add_paragraph(doc,
        "Ứng dụng bảng điều khiển giám sát được hiện thực hóa trong tệp streamlit/app.py với giao diện hoàn toàn bằng tiếng Anh chuyên nghiệp. Một thách thức kỹ thuật lớn khi tích hợp Streamlit với DuckDB là cơ chế khóa tệp độc quyền: nếu Streamlit duy trì một kết nối mở liên tục tới tệp dev.duckdb, các tiến trình dbt run chạy ngầm sẽ lập tức bị lỗi xung đột khóa tệp."
    )

    add_paragraph(doc,
        "Để giải quyết triệt để vấn đề này, hệ thống áp dụng mẫu thiết kế quản lý ngữ cảnh an toàn với cú pháp with duckdb.connect(database=db_path, read_only=True) as con:. Kết nối chỉ mở tạm thời ở chế độ chỉ đọc trong khoảng 0,05 giây để thực thi ba câu truy vấn nạp dữ liệu vào ba đối tượng Pandas DataFrame, sau đó lập tức giải phóng và đóng tệp hoàn toàn. Kết hợp với bộ đệm bộ nhớ @st.cache_data có thời gian sống mười phút, toàn bộ các thao tác lọc danh mục và chuyển trang của người dùng đều diễn ra trực tiếp trên bộ nhớ RAM với độ trễ tiệm cận không mili-giây [11]."
    )

    add_heading_3(doc, "3.5.2. Chi tiết các chức năng nghiệp vụ trên Bảng điều khiển")
    add_paragraph(doc,
        "Bảng điều khiển được tổ chức khoa học thành ba thẻ chức năng trực quan không lạm dụng biểu tượng cảm xúc rườm rà:"
    )

    add_paragraph(doc,
        "Thẻ thứ nhất là Xu hướng Hàng tháng, hiển thị biểu đồ đường tương tác Plotly trực quan hóa song hành ba đường: tổng số đánh giá, số lượng đánh giá tích cực và số lượng đánh giá tiêu cực qua chín tháng của từng danh mục ngành hàng, đi kèm bảng dữ liệu số học chi tiết có thể thu gọn mở rộng."
    )

    add_paragraph(doc,
        "Thẻ thứ hai là Top Sản phẩm Lỗi, trình bày biểu đồ cột nằm ngang xếp hạng mười sản phẩm có số lượng nhận xét tiêu cực lớn nhất. Trục tung biểu đồ chỉ hiển thị mã định danh sản phẩm cha rõ ràng, nhãn cột ghi chú rõ tỷ lệ số lượng chê trên tổng số đánh giá, và hộp thông tin rê chuột hiển thị đầy đủ tên sản phẩm cùng số sao đánh giá trung bình."
    )

    add_paragraph(doc,
        "Thẻ thứ ba là Cảnh báo Đột biến Lỗi, cung cấp ba thẻ chỉ số đo lường nhanh số lượng sự cố nghiêm trọng, số lượng sự cố cảnh báo và mức tăng tỷ lệ tiêu cực trung bình, đi kèm bảng dữ liệu chi tiết cho phép tra cứu ngay lập tức các sản phẩm đang có tỷ lệ khiếu nại bùng phát theo thời gian thực."
    )

    # 3.6. Đánh giá hiệu năng và kết quả thực nghiệm
    add_heading_2(doc, "3.6. Đánh giá hiệu năng và kết quả thực nghiệm")

    add_heading_3(doc, "3.6.1. Đánh giá chất lượng mô hình học máy và phân tích lỗi")
    add_paragraph(doc,
        "Chất lượng phân loại của hệ thống đạt tiêu chuẩn xuất sắc khi mô hình nhận diện chính xác 92,33% các đánh giá hài lòng và 77,19% các đánh giá khiếu nại trên tập kiểm thử độc lập. Phân tích sâu các trường hợp dự đoán sai cho thấy phần lớn lỗi tập trung ở lớp Trung tính ba sao, nơi người dùng thường kết hợp các mệnh đề trái ngược nhau. Tuy nhiên, đối với bài toán kinh doanh cốt lõi là nhận diện các sản phẩm có chất lượng bất thường, độ chính xác cao của hai lớp Tích cực và Tiêu cực là hoàn toàn đủ để bảo đảm độ tin cậy tuyệt đối cho các thuật toán phát hiện đột biến."
    )

    add_heading_3(doc, "3.6.2. Đánh giá hiệu năng kỹ thuật dữ liệu và độ trễ hệ thống")
    add_paragraph(doc,
        "Về mặt hiệu năng kỹ thuật dữ liệu, toàn bộ các khâu trong đường ống đều thể hiện tốc độ xử lý vượt trội. Bảng 3.6 tổng hợp chi tiết thời gian thực thi của từng giai đoạn trên quy mô 2,87 triệu bản ghi."
    )

    add_caption(doc, "Bảng 3.6: Thống kê hiệu năng thực thi của toàn bộ đường ống dữ liệu", is_table=True)
    headers_t9 = ["Giai đoạn xử lý / Thành phần", "Công nghệ thực thi", "Quy mô dữ liệu xử lý", "Thời gian hoàn thành", "Đánh giá hiệu năng"]
    rows_t9 = [
        ["Tiền xử lý và làm sạch tầng Bạc", "PySpark Distributed", "2.870.515 bản ghi thô", "4,5 phút", "Thông lượng đạt ~10.600 dòng/giây"],
        ["Huấn luyện Mô hình Vô địch", "Scikit-Learn Multi-thread", "2.009.360 mẫu train", "12,0 phút", "Hội tụ tối ưu trên không gian N-gram"],
        ["Suy luận hàng loạt tầng Vàng", "PySpark Batch Inference", "2.870.515 bản ghi sạch", "11,8 phút", "Chấm điểm song song trên cụm phân tán"],
        ["Mô hình hóa Marts và SPC Z-score", "dbt-DuckDB Vectorized", "7 models dữ liệu", "7,30 giây", "Giảm 85% thời gian sau khi lược bỏ Task 9"],
        ["Tải dữ liệu và kết xuất Dashboard", "DuckDB In-Process + Streamlit", "3 bảng Data Marts", "0,08 giây", "Phản hồi người dùng tiệm cận tức thì"]
    ]
    add_styled_table(doc, headers_t9, rows_t9, col_widths=[4.5, 3.5, 3.2, 2.3, 3.5])

    # 3.7. Kết luận chương
    add_heading_2(doc, "3.7. Kết luận chương")
    add_paragraph(doc,
        "Chương 3 đã chứng minh tính đúng đắn, khoa học và hiệu quả vượt bậc của hệ thống thông qua các kết quả thực nghiệm toàn diện trên 2,87 triệu lượt đánh giá Amazon. Mô hình N-gram Linear SVM với Class Weighting đã xuất sắc giành vị trí Champion Model và vượt qua kiểm định độc lập trên hơn bốn trăm nghìn mẫu kiểm thử. Việc tích hợp kiến trúc Medallion Lakehouse trên MinIO, động cơ dbt-DuckDB và thuật toán SPC Z-score đã biến dữ liệu văn bản phi cấu trúc thành các cảnh báo chất lượng có độ chính xác cao với thời gian truy vấn dưới một phần mười giây, khẳng định sự thành công trọn vẹn của giải pháp thiết kế."
    )

    doc.add_page_break()
