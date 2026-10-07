"""
chapter1.py: Triển khai nội dung CHƯƠNG 1 - TỔNG QUAN VỀ ĐỀ TÀI VÀ CƠ SỞ DỮ LIỆU.
Bao gồm:
- 1.1 Tính cấp thiết của đề tài
- 1.2 Mục tiêu nghiên cứu (1.2.1 Mục tiêu tổng quát, 1.2.2 Mục tiêu kỹ thuật)
- 1.3 Đối tượng và phạm vi nghiên cứu (1.3.1 Dữ liệu đánh giá, 1.3.2 Dữ liệu metadata, 1.3.3 Thách thức dữ liệu thực tế)
- 1.4 Kết luận chương 1
"""

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_generator.styles import (
    add_paragraph, add_heading_1, add_heading_2, add_heading_3,
    add_caption, add_styled_table
)


def build_chapter_1(doc):
    """Xây dựng toàn bộ nội dung Chương 1."""
    add_heading_1(doc, "CHƯƠNG 1. TỔNG QUAN VỀ ĐỀ TÀI VÀ CƠ SỞ DỮ LIỆU")

    add_paragraph(doc,
        "Chương 1 trình bày tổng quan bối cảnh nghiên cứu, phân tích tính cấp thiết xuất phát từ thực tiễn sản xuất kinh doanh thương mại điện tử, xác định rõ ràng mục tiêu tổng quát cùng các mục tiêu kỹ thuật cụ thể của đề tài. Đồng thời, chương này tiến hành khảo sát và mổ xẻ chi tiết cấu trúc tập dữ liệu đánh giá thương mại điện tử Amazon Reviews 2023, phân tích các trường thông tin then chốt và chỉ ra những thách thức cố hữu của dữ liệu thực tế làm nền tảng khoa học cho toàn bộ hệ thống xử lý phía sau [1], [5]."
    )

    # 1.1. Tính cấp thiết của đề tài
    add_heading_2(doc, "1.1. Tính cấp thiết của đề tài")

    add_paragraph(doc,
        "Thương mại điện tử hiện đại đã và đang trở thành huyết mạch của nền kinh tế số toàn cầu. Sự phổ cập của các sàn giao dịch quy mô lớn như Amazon, Shopee hay Alibaba cho phép hàng trăm triệu người tiêu dùng chia sẻ cảm nhận, trải nghiệm và đánh giá chất lượng sản phẩm chỉ bằng vài cú nhấp chuột. Khác với các cuộc điều tra khảo sát thị trường truyền thống vốn tốn kém nhiều tháng thực hiện và dễ bị chi phối bởi độ lệch chọn mẫu, các bản đánh giá trực tuyến cung cấp một bức tranh toàn diện, khách quan và tức thì về hành vi người dùng. Nguồn dữ liệu này phản ánh trung thực cách khách hàng tiếp nhận sản phẩm, từ chất lượng bao bì đóng gói, độ bền vật lý, mức độ tương thích chức năng cho tới thái độ phục vụ của người bán hàng [2]."
    )

    add_paragraph(doc,
        "Mặc dù mang giá trị chiến lược to lớn, các doanh nghiệp kinh doanh trên nền tảng số hiện nay lại đang đối mặt với nghịch lý thừa mứa dữ liệu nhưng thiếu hụt tri thức hành động. Tốc độ sản sinh dữ liệu hàng nghìn lượt đánh giá mới mỗi ngày trên mỗi danh mục ngành hàng tạo nên áp lực quá tải vượt xa năng lực giám sát thủ công của các nhóm kiểm soát chất lượng và dịch vụ khách hàng. Hậu quả trực tiếp là thời gian phát hiện lỗi kỹ thuật của sản phẩm bị kéo dài đáng kể. Doanh nghiệp thường rơi vào tình huống bị động, chỉ nhận ra một lô hàng bị hỏng hóc gia công hoặc bị khiếm khuyết linh kiện khi làn sóng đánh giá tiêu cực một sao và hai sao đã bùng phát dữ dội trên hệ thống, kéo theo tỷ lệ yêu cầu hoàn tiền và hủy đơn hàng tăng vọt [3]."
    )

    add_paragraph(doc,
        "Hơn thế nữa, sự lan truyền nhanh chóng của tâm lý đám đông trên môi trường trực tuyến có thể biến một lỗi kỹ thuật đơn lẻ thành một cuộc khủng hoảng truyền thông thương hiệu trầm trọng chỉ trong vài ngày. Việc sụt giảm điểm số đánh giá trung bình không chỉ đẩy sản phẩm xuống vị trí cuối cùng trong thuật toán đề xuất tìm kiếm của sàn thương mại điện tử mà còn làm suy giảm vĩnh viễn niềm tin của khách hàng trung thành. Do đó, việc xây dựng một hệ thống kỹ thuật có khả năng tự động hóa việc thu thập, phân tích sắc thái cảm xúc ở quy mô lớn, phát hiện sớm các bất thường trong tỷ lệ chê theo chuỗi thời gian là bài toán sống còn đối với sự phát triển bền vững của doanh nghiệp số hiện đại [4]."
    )

    # 1.2. Mục tiêu nghiên cứu
    add_heading_2(doc, "1.2. Mục tiêu nghiên cứu")

    add_heading_3(doc, "1.2.1. Mục tiêu tổng quát")
    add_paragraph(doc,
        "Mục tiêu bao trùm của đề tài là thiết kế, xây dựng và hoàn thiện một hệ thống xử lý dữ liệu lớn toàn diện theo mô hình Data Pipeline phân tán, tự động hóa từ đầu đến cuối quy trình tiếp nhận dữ liệu thô, chuẩn hóa, phân loại cảm xúc văn bản, mô hình hóa xu hướng theo chuỗi thời gian, và tự động cảnh báo các sản phẩm có dấu hiệu lỗi đột biến. Hệ thống đảm bảo tính mở, khả năng chịu lỗi cao, hiệu năng tính toán xuất sắc và sẵn sàng mở rộng quy mô khi dung lượng dữ liệu tăng từ vài gigabyte lên hàng chục gigabyte trong môi trường sản xuất thực tế [1], [6]."
    )

    add_paragraph(doc,
        "Về mặt kiến trúc, hệ thống hiện thực hóa mô hình Medallion Lakehouse ba tầng chuẩn hóa gồm tầng Đồng lưu trữ dữ liệu nguyên bản, tầng Bạc lưu trữ dữ liệu đã làm sạch và tầng Vàng lưu trữ các bảng dữ liệu nghiệp vụ đã được làm giàu bởi mô hình học máy. Việc tổ chức này giúp tách biệt rành mạch giữa lớp lưu trữ và lớp tính toán, bảo toàn tính toàn vẹn của dữ liệu gốc đồng thời tối ưu hóa tài nguyên phần cứng cho các tác vụ phân tích nâng cao tiếp theo [7]."
    )

    add_heading_3(doc, "1.2.2. Mục tiêu kỹ thuật cụ thể")
    add_paragraph(doc,
        "Để hiện thực hóa mục tiêu tổng quát, đề tài xác định và giải quyết triệt để sáu mục tiêu kỹ thuật chuyên sâu sau đây:"
    )

    add_paragraph(doc,
        "Mục tiêu thứ nhất, thiết lập hạ tầng lưu trữ Data Lakehouse ba tầng phân tán trên nền tảng lưu trữ đối tượng MinIO tương thích hoàn toàn với giao thức AWS S3. Hạ tầng này đảm bảo khả năng mở rộng không giới hạn về dung lượng và cho phép các tác vụ tính toán truy cập đồng thời với thông lượng cao [6]."
    )

    add_paragraph(doc,
        "Mục tiêu thứ hai, phát triển pipeline tiền xử lý và làm sạch dữ liệu quy mô lớn bằng Apache Spark và giao diện lập trình PySpark. Pipeline có nhiệm vụ chuẩn hóa cấu trúc văn bản, loại bỏ các ký tự đặc biệt gây nhiễu, xử lý triệt để các trường dữ liệu rỗng và khử trùng lặp bản ghi trên toàn bộ tập dữ liệu hơn 2,87 triệu lượt đánh giá [8]."
    )

    add_paragraph(doc,
        "Mục tiêu thứ ba, nghiên cứu thực nghiệm và xây dựng một Sentiment Engine chuẩn xác cao độ để phân loại văn bản theo ba lớp cảm xúc gồm Tích cực, Trung tính và Tiêu cực. Mô hình phải giải quyết thấu đáo vấn đề mất cân bằng dữ liệu nghiêm trọng giữa các lớp và khai thác tối đa ngữ cảnh của các cụm từ phủ định thông qua kỹ thuật trích xuất đặc trưng N-gram bậc hai kết hợp thuật toán Linear SVM [9]."
    )

    add_paragraph(doc,
        "Mục tiêu thứ tư, triển khai quy trình suy luận hàng loạt theo lô quy mô lớn trên Apache Spark, thực hiện gán nhãn cảm xúc và tính toán điểm số khoảng cách siêu phẳng cho toàn bộ 2,87 triệu đánh giá, lưu trữ kết quả vào bảng dữ liệu cốt lõi tại tầng Vàng dưới định dạng Parquet nén Snappy [7]."
    )

    add_paragraph(doc,
        "Mục tiêu thứ năm, ứng dụng công cụ mô hình hóa dữ liệu dbt kết hợp hệ quản trị cơ sở dữ liệu phân tích DuckDB để xây dựng các bảng dữ liệu nghiệp vụ phục vụ phân tích xu hướng. Triển khai thuật toán kiểm soát quá trình bằng thống kê với cửa sổ trượt ba tháng quá khứ để phát hiện các sản phẩm bị đột biến tỷ lệ khiếu nại dựa trên chỉ số Z-score [10]."
    )

    add_paragraph(doc,
        "Mục tiêu thứ sáu, hoàn thiện ứng dụng bảng điều khiển giám sát tương tác bằng thư viện Streamlit, kết hợp cơ chế bộ đệm trong bộ nhớ và truy vấn DuckDB chỉ đọc nhằm cung cấp trải nghiệm theo dõi xu hướng, truy vết sản phẩm lỗi với độ trễ phản hồi dưới 0,1 giây [11]."
    )

    # 1.3. Đối tượng và phạm vi nghiên cứu
    add_heading_2(doc, "1.3. Đối tượng và phạm vi nghiên cứu")

    add_paragraph(doc,
        "Đối tượng nghiên cứu của đề tài là tập dữ liệu văn bản thương mại điện tử Amazon Reviews 2023 do nhóm nghiên cứu McAuley Lab thuộc Đại học California tại San Diego công bố và chuẩn hóa. Đây là một trong những tập dữ liệu học thuật quy mô lớn nhất hiện nay về hành vi người dùng, phản ánh đa dạng ngôn ngữ tự nhiên đời thực của khách hàng mua sắm trực tuyến [5]."
    )

    add_paragraph(doc,
        "Về phạm vi nghiên cứu, đề tài tập trung chuyên sâu vào hai danh mục sản phẩm trọng yếu đại diện cho ngành hàng tiêu dùng nhanh và thời trang là All_Beauty và Amazon_Fashion. Toàn bộ các đánh giá được phân tích nằm trong chuỗi thời gian chín tháng liên tục của năm 2023, từ tháng 1 đến tháng 9, với tổng số 2.870.515 bản ghi đánh giá hoàn chỉnh. Hệ thống tập trung giải quyết bài toán phân loại ba trạng thái cảm xúc cốt lõi và phát hiện sự cố chất lượng theo mô hình xử lý theo lô định kỳ."
    )

    add_heading_3(doc, "1.3.1. Cấu trúc tập dữ liệu đánh giá người dùng")
    add_paragraph(doc,
        "Tập dữ liệu đánh giá người dùng được lưu trữ dưới định dạng các tệp JSON thô nén GZIP, trong đó mỗi dòng biểu diễn một giao dịch đánh giá hoàn chỉnh. Bảng 1.1 mô tả chi tiết lược đồ dữ liệu, kiểu dữ liệu và ý nghĩa nghiệp vụ của từng trường thông tin cốt lõi trong tập dữ liệu."
    )

    add_caption(doc, "Bảng 1.1: Cấu trúc các trường thông tin trong tập dữ liệu Amazon Reviews 2023", is_table=True)
    headers_t1 = ["Tên trường dữ liệu", "Kiểu dữ liệu", "Mô tả nghiệp vụ", "Vai trò trong hệ thống"]
    rows_t1 = [
        ["rating", "Float / Double", "Điểm số đánh giá từ 1.0 đến 5.0 sao", "Cơ sở sinh nhãn giả lập mặt đất phục vụ huấn luyện"],
        ["title", "String", "Tiêu đề tóm tắt ngắn gọn của bài đánh giá", "Kết hợp với nội dung chính để tạo văn bản hoàn chỉnh"],
        ["text", "String", "Nội dung chi tiết của bản nhận xét đánh giá", "Đặc trưng đầu vào cốt lõi cho mô hình xử lý ngôn ngữ"],
        ["parent_asin", "String", "Mã định danh sản phẩm chung cấp độ cha", "Khóa chính để gom nhóm và theo dõi vòng đời sản phẩm"],
        ["asin", "String", "Mã sản phẩm con theo kích thước hoặc màu sắc", "Thông tin định danh biến thể sản phẩm chi tiết"],
        ["user_id", "String", "Mã định danh duy nhất của người dùng", "Kiểm tra tần suất người dùng và ngăn chặn đánh giá giả mạo"],
        ["timestamp", "Long / Timestamp", "Mốc thời gian gửi đánh giá theo chuẩn Unix epoch", "Trục thời gian để phân tích xu hướng và tính cửa sổ trượt"],
        ["helpful_vote", "Integer", "Số lượt người dùng khác bình chọn đánh giá hữu ích", "Đánh giá mức độ ảnh hưởng của nhận xét tiêu cực"],
        ["verified_purchase", "Boolean", "Cờ xác nhận người đánh giá đã thực sự mua hàng", "Bộ lọc đảm bảo độ tin cậy của phản hồi thực tế"]
    ]
    add_styled_table(doc, headers_t1, rows_t1, col_widths=[3.5, 3.0, 5.5, 4.0])

    add_heading_3(doc, "1.3.2. Cấu trúc tập dữ liệu mô tả sản phẩm")
    add_paragraph(doc,
        "Song hành cùng dữ liệu đánh giá, tập dữ liệu metadata sản phẩm cung cấp các thuộc tính tĩnh và thông tin mô tả chi tiết về từng mặt hàng. Dữ liệu này đóng vai trò then chốt tại tầng Vàng, cho phép ghép nối mã định danh sản phẩm với tên gọi thân thiện, thương hiệu và mức giá hiển thị trên giao diện người dùng. Bảng 1.2 trình bày lược đồ chi tiết của tập dữ liệu này."
    )

    add_caption(doc, "Bảng 1.2: Cấu trúc các trường thông tin trong tập dữ liệu Product Metadata", is_table=True)
    headers_t2 = ["Tên trường dữ liệu", "Kiểu dữ liệu", "Mô tả nghiệp vụ", "Vai trò trong hệ thống"]
    rows_t2 = [
        ["parent_asin", "String", "Mã định danh sản phẩm cha", "Khóa ngoại ghép nối trực tiếp với bảng dữ liệu đánh giá"],
        ["title", "String", "Tên hiển thị đầy đủ của sản phẩm", "Hiển thị ngữ cảnh kinh doanh rõ ràng trên bảng điều khiển"],
        ["main_category", "String", "Danh mục phân loại chính của sản phẩm", "Phân khúc ngành hàng phục vụ các chỉ số tổng hợp cấp vĩ mô"],
        ["average_rating", "Float", "Điểm số đánh giá trung bình tích lũy toàn sàn", "Chỉ số tham chiếu đối sánh với điểm số tính toán nội bộ"],
        ["rating_number", "Integer", "Tổng số lượt đánh giá tích lũy lịch sử", "Ngưỡng lọc loại bỏ các sản phẩm mới có quá ít dữ liệu"],
        ["features", "Array / List", "Danh sách các đặc tính kỹ thuật sản phẩm", "Thông tin bổ trợ phục vụ phân tích ngữ cảnh chuyên sâu"],
        ["price", "Float / String", "Mức giá niêm yết của mặt hàng", "Phân tích mối tương quan giữa mức giá và tỷ lệ phàn nàn"],
        ["store", "String", "Tên thương hiệu hoặc cửa hàng phân phối", "Nhận diện các nhà cung cấp có tỷ lệ sản phẩm lỗi cao"]
    ]
    add_styled_table(doc, headers_t2, rows_t2, col_widths=[3.5, 3.0, 5.5, 4.0])

    add_heading_3(doc, "1.3.3. Thách thức cố hữu của dữ liệu thực tế")
    add_paragraph(doc,
        "Trong quá trình khảo sát và phân tích khám phá dữ liệu, nhóm nghiên cứu nhận diện ba thách thức kỹ thuật lớn nhất mang tính cố hữu của dữ liệu đánh giá thương mại điện tử quy mô lớn:"
    )

    add_paragraph(doc,
        "Thách thức đầu tiên là sự mất cân bằng lớp trầm trọng trong phân phối đánh giá. Trong môi trường bán lẻ trực tuyến, khách hàng có xu hướng chỉ để lại phản hồi khi họ cực kỳ hài lòng với sản phẩm, dẫn đến việc các đánh giá bốn sao và năm sao chiếm tỷ trọng áp đảo lên tới trên 70% tổng số mẫu. Ngược lại, các đánh giá tiêu cực một sao và hai sao chỉ chiếm khoảng 20%, trong khi lớp đánh giá trung tính ba sao chỉ chiếm dưới 10%. Hiện tượng này đặt ra rủi ro rất lớn khiến các thuật toán học máy thiên vị về lớp đa số, làm suy giảm nghiêm trọng khả năng nhận diện lớp thiểu số là lớp mang giá trị cảnh báo rủi ro cao nhất [9]."
    )

    add_paragraph(doc,
        "Thách thức thứ hai là độ nhiễu cao và tính phi cấu trúc phức tạp của văn bản. Người tiêu dùng sử dụng ngôn ngữ tự do với nhiều từ viết tắt, lỗi chính tả, teencode, tiếng lóng, và sự pha trộn giữa các ngôn ngữ khác nhau. Đáng chú ý, các đánh giá ba sao thường mang tính chất cảm xúc hỗn hợp, ví dụ như người dùng khen ngợi chất lượng vải nhưng phàn nàn gay gắt về khóa kéo bị hỏng. Sự phức tạp này khiến các mô hình phân loại truyền thống dễ bị bối rối nếu không được trang bị kỹ thuật phân tích cụm từ và ngữ cảnh phù hợp."
    )

    add_paragraph(doc,
        "Thách thức thứ ba là nguy cơ rò rỉ dữ liệu giữa tập huấn luyện và tập kiểm định do hiện tượng trùng lặp văn bản. Rất nhiều người dùng sao chép lại nhận xét có sẵn hoặc người bán sử dụng các công cụ tạo đánh giá tự động tạo ra hàng chục nghìn bản ghi có nội dung giống hệt nhau. Nếu chia tập dữ liệu ngẫu nhiên thông thường mà không kiểm tra mã băm nội dung, các văn bản trong tập huấn luyện sẽ rò rỉ sang tập kiểm tra, dẫn đến việc đo lường độ chính xác bị thổi phồng giả tạo và mô hình thất bại hoàn toàn khi triển khai trên dữ liệu mới [12]."
    )

    # 1.4. Kết luận chương
    add_heading_2(doc, "1.4. Kết luận chương")
    add_paragraph(doc,
        "Chương 1 đã thiết lập bức tranh tổng thể và nền tảng khoa học vững chắc cho toàn bộ đề tài. Qua việc phân tích tính cấp thiết của bài toán giám sát tâm lý khách hàng và xác định cụ thể các mục tiêu kỹ thuật, đề tài đã làm rõ phạm vi nghiên cứu trên tập dữ liệu Amazon Reviews 2023 với quy mô 2,87 triệu lượt đánh giá. Những phân tích chi tiết về lược đồ dữ liệu và các thách thức về mất cân bằng lớp, độ nhiễu văn bản cùng rò rỉ dữ liệu là cơ sở trực tiếp để định hình các giải pháp kiến trúc và thuật toán chuyên sâu được trình bày trong Chương 2 và Chương 3 tiếp theo."
    )

    doc.add_page_break()
