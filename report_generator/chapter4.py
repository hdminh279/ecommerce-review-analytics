"""
chapter4.py: Triển khai nội dung CHƯƠNG 4 - KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN
và Danh mục TÀI LIỆU THAM KHẢO chuẩn IEEE.
"""

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_generator.styles import (
    add_paragraph, add_heading_1, add_heading_2, add_heading_3
)


def build_chapter_4_and_references(doc):
    """Xây dựng nội dung Chương 4 và Danh mục Tài liệu tham khảo."""
    add_heading_1(doc, "CHƯƠNG 4. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")

    add_paragraph(doc,
        "Chương 4 tổng kết toàn diện các kết quả lý thuyết và thực nghiệm đã đạt được của đề tài, đánh giá mức độ hoàn thành nhiệm vụ nghiên cứu so với các mục tiêu ban đầu đề ra, phân tích khách quan các giới hạn kỹ thuật còn tồn tại, và đề xuất các định hướng mở rộng hệ thống có giá trị ứng dụng cao trong tương lai [1], [6]."
    )

    # 4.1. Kết quả đạt được
    add_heading_2(doc, "4.1. Kết quả đạt được của đề tài")
    add_paragraph(doc,
        "Sau quá trình nghiên cứu lý thuyết chuyên sâu, thiết kế kiến trúc và triển khai thực nghiệm toàn diện trên tập dữ liệu thương mại điện tử thực tế, đề tài đã hoàn thành xuất sắc toàn bộ các mục tiêu đặt ra với những đóng góp cụ thể sau đây:"
    )

    add_paragraph(doc,
        "Thứ nhất, về mặt hạ tầng và kỹ thuật dữ liệu, đề tài đã xây dựng thành công một hệ thống Data Pipeline phân tán theo kiến trúc Medallion Lakehouse ba tầng chuẩn mực trên hệ thống lưu trữ đối tượng MinIO. Đường ống xử lý PySpark vận hành ổn định, thực hiện tiền xử lý, khử trùng lặp và làm sạch 2.870.515 bản ghi thô chỉ trong 4,5 phút, đạt thông lượng hơn mười nghìn dòng mỗi giây, lưu trữ tối ưu dưới định dạng cột Parquet nén Snappy."
    )

    add_paragraph(doc,
        "Thứ hai, về mặt học máy xử lý ngôn ngữ tự nhiên, đề tài đã tiến hành đối chuẩn thực nghiệm khắt khe bảy phương pháp phân loại khác nhau trên tập kiểm định gồm 429.668 mẫu. Mô hình kết hợp đặc trưng N-gram bậc hai với thuật toán Linear SVM và kỹ thuật điều chỉnh trọng số Class Weighting đã xuất sắc được lựa chọn làm Mô hình Vô địch. Khi kiểm thử độc lập trên 431.487 mẫu dữ liệu chưa từng nhìn thấy, mô hình đạt độ chính xác 83,62%, nhận diện đúng 92,33% các nhận xét tích cực và 77,19% các nhận xét tiêu cực, hoàn tất tác vụ suy luận hàng loạt cho gần ba triệu bản ghi trong chưa đầy mười hai phút."
    )

    add_paragraph(doc,
        "Thứ ba, về mặt mô hình hóa nghiệp vụ và phát hiện sự cố, hệ thống đã ứng dụng sáng tạo bộ đôi công nghệ dbt và DuckDB, xây dựng ba bảng dữ liệu Marts chuyên sâu với thời gian thực thi chỉ 7,30 giây. Thuật toán kiểm soát quá trình bằng thống kê với cửa sổ trượt ba tháng quá khứ đã phát hiện chính xác 556 sự cố đột biến tỷ lệ khiếu nại thực tế, phân cấp rủi ro rõ ràng thành hai cấp độ cảnh báo để hỗ trợ nhà quản trị can thiệp kịp thời."
    )

    add_paragraph(doc,
        "Thứ tư, về mặt ứng dụng phục vụ người dùng, ứng dụng bảng điều khiển giám sát Streamlit đã được hoàn thiện với giao diện tiếng Anh trang nhã, áp dụng cơ chế truy vấn DuckDB chỉ đọc không khóa tệp và lưu đệm bộ nhớ RAM, mang lại trải nghiệm khám phá dữ liệu mượt mà với độ trễ phản hồi dưới 0,08 giây."
    )

    # 4.2. Hạn chế
    add_heading_2(doc, "4.2. Những hạn chế còn tồn tại")
    add_paragraph(doc,
        "Bên cạnh những thành tựu nổi bật, nghiên cứu vẫn còn một số điểm hạn chế kỹ thuật cần được nhìn nhận khách quan:"
    )

    add_paragraph(doc,
        "Hạn chế thứ nhất nằm ở phạm vi bao phủ dữ liệu. Do giới hạn về tài nguyên máy tính phục vụ huấn luyện mô hình học máy phân tán, phạm vi nghiên cứu thực nghiệm hiện chỉ tập trung vào hai ngành hàng là All_Beauty và Amazon_Fashion trong chín tháng của năm 2023. Hệ thống chưa được kiểm thử toàn diện trên tất cả hơn ba mươi danh mục sản phẩm khác nhau của sàn Amazon."
    )

    add_paragraph(doc,
        "Hạn chế thứ hai liên quan đến độ chính xác phân loại của lớp cảm xúc Trung tính ba sao. Mặc dù đã áp dụng trọng số chi phí và N-gram bậc hai, điểm số F1 của lớp này chỉ đạt 42,81% do tính chất pha trộn phức tạp giữa khen và chê trong cùng một câu văn. Điều này đòi hỏi các mô hình ngữ cảnh sâu hơn để bóc tách từng vế câu đối lập."
    )

    add_paragraph(doc,
        "Hạn chế thứ ba là phương pháp thiết lập ngưỡng kích hoạt cảnh báo đột biến Z-score hiện vẫn dựa trên các ngưỡng bán tự động tĩnh như Z lớn hơn hoặc bằng 2,0 và mức tăng tối thiểu mười lăm điểm phần trăm. Trong thực tế, các danh mục ngành hàng có biên độ dao động tự nhiên rất khác nhau, đòi hỏi một cơ chế tự động học ngưỡng động thích ứng cho từng nhóm sản phẩm."
    )

    # 4.3. Hướng phát triển
    add_heading_2(doc, "4.3. Hướng nghiên cứu và phát triển tiếp theo")
    add_paragraph(doc,
        "Để hoàn thiện hệ thống và đưa giải pháp vào ứng dụng thương mại thực tế ở quy mô công nghiệp, các hướng phát triển ưu tiên trong tương lai bao gồm:"
    )

    add_paragraph(doc,
        "Một là, mở rộng quy mô đường ống dữ liệu để bao phủ toàn bộ kho dữ liệu đánh giá Amazon với hơn ba mươi triệu bản ghi, tích hợp công cụ điều phối luồng tự động Apache Airflow để định kỳ kích hoạt các tác vụ trích xuất, làm sạch, suy luận và cập nhật báo cáo tự động mỗi ngày mà không cần sự can thiệp thủ công."
    )

    add_paragraph(doc,
        "Hai là, nghiên cứu tích hợp các mô hình ngôn ngữ lớn hoặc mô hình ngôn ngữ nhỏ cục bộ ở chế độ suy luận chọn lọc. Cụ thể, khi thuật toán SPC Z-score phát hiện một sản phẩm rơi vào trạng thái Đột biến Nghiêm trọng, hệ thống sẽ tự động chuyển một tập hợp các đánh giá tiêu cực tiêu biểu của sản phẩm đó tới mô hình ngôn ngữ để tự động tóm tắt nguyên nhân gốc rễ thành một bản báo cáo ngắn gọn, giải thích rõ sản phẩm bị lỗi ở linh kiện nào, giúp bộ phận kỹ thuật khắc phục sự cố ngay lập tức."
    )

    add_paragraph(doc,
        "Ba là, nâng cấp đường ống xử lý theo lô hiện tại sang kiến trúc xử lý dữ liệu dòng thời gian thực bằng cách kết hợp Apache Kafka và Spark Structured Streaming, cho phép hệ thống phân tích và phát hiện các phản hồi tiêu cực nguy hiểm chỉ trong vài phút sau khi khách hàng đăng tải đánh giá lên sàn thương mại điện tử."
    )

    doc.add_page_break()

    # TÀI LIỆU THAM KHẢO
    add_heading_1(doc, "TÀI LIỆU THAM KHẢO")

    references_list = [
        "[1] J. McAuley, Y. Hou, W. C. Kang, and J. Li, \"Amazon Review Data (2023),\" University of California San Diego (UCSD) McAuley Lab, Technical Report, 2023. [Online]. Available: https://datarepo.eng.ucsd.edu/mcauley_group/data/amazon_2023/",
        "[2] N. Hu, L. Liu, and J. Zhang, \"Do online reviews affect product sales? The role of reviewer characteristics and temporal effects,\" Information Technology and Management, vol. 9, no. 3, pp. 201–214, 2008. DOI: 10.1007/s10799-008-0041-2.",
        "[3] S. M. Mudambi and D. Schuff, \"What makes a helpful online review? A study of customer reviews on Amazon.com,\" MIS Quarterly, vol. 34, no. 1, pp. 185–200, 2010. DOI: 10.2307/20721420.",
        "[4] B. Pang and L. Lee, \"Opinion mining and sentiment analysis,\" Foundations and Trends in Information Retrieval, vol. 2, no. 1–2, pp. 1–135, 2008. DOI: 10.1561/1500000011.",
        "[5] Y. Hou, J. Li, Z. He, A. Yan, X. Chen, and J. McAuley, \"Bridging Language and Items for Retrieval and Recommendation,\" in Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '24), 2024, pp. 1543–1553. DOI: 10.1145/3626772.3657828.",
        "[6] Samsung Innovation Campus, \"Big Data Course Curriculum & Technical Lecture Series (Chapters 1–11),\" Samsung Electronics Global Training Materials, 2024.",
        "[7] M. Zaharia, M. Chowdhury, T. Das, A. Dave, J. Ma, M. McCauley, M. J. Franklin, S. Shenker, and I. Stoica, \"Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing,\" in Proceedings of the 9th USENIX Symposium on Networked Systems Design and Implementation (NSDI '12), San Jose, CA, 2012, pp. 15–28.",
        "[8] B. Chambers and M. Zaharia, Spark: The Definitive Guide - Big Data Processing Made Simple, 1st ed. Sebastopol, CA: O'Reilly Media, 2018. ISBN: 978-1491912218.",
        "[9] C. Cortes and V. Vapnik, \"Support-Vector Networks,\" Machine Learning, vol. 20, no. 3, pp. 273–297, 1995. DOI: 10.1007/BF00994018.",
        "[10] D. C. Montgomery, Introduction to Statistical Quality Control, 8th ed. Hoboken, NJ: John Wiley & Sons, 2019. ISBN: 978-1119398851.",
        "[11] M. Armbrust, A. Ghodsi, R. Xin, and M. Zaharia, \"Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics,\" in Proceedings of the 11th Conference on Innovative Data Systems Research (CIDR '21), Chaminade, HI, 2021.",
        "[12] N. Japkowicz and S. Stephen, \"The class imbalance problem: A systematic study,\" Intelligent Data Analysis, vol. 6, no. 5, pp. 429–449, 2002. DOI: 10.3233/IDA-2002-6504.",
        "[13] G. Salton and C. Buckley, \"Term-weighting approaches in automatic text retrieval,\" Information Processing & Management, vol. 24, no. 5, pp. 513–523, 1988. DOI: 10.1016/0306-4573(88)90021-0.",
        "[14] J. Dean and S. Ghemawat, \"MapReduce: Simplified Data Processing on Large Clusters,\" in Proceedings of the 6th Symposium on Operating System Design and Implementation (OSDI '04), San Francisco, CA, 2004, pp. 137–150.",
        "[15] M. Armbrust, R. S. Xin, C. Lian, Y. Huai, D. Liu, J. K. Bradley, X. Meng, T. Kaftan, M. J. Franklin, A. Ghodsi, and M. Zaharia, \"Spark SQL: Relational Data Processing in Spark,\" in Proceedings of the 2015 ACM SIGMOD International Conference on Management of Data, Melbourne, Australia, 2015, pp. 1383–1394. DOI: 10.1145/2723372.2742797.",
        "[16] M. Raasveldt and H. Mühleisen, \"DuckDB: an Embeddable Analytical Database,\" in Proceedings of the 2019 ACM SIGMOD International Conference on Management of Data, Amsterdam, Netherlands, 2019, pp. 1981–1984. DOI: 10.1145/3329785.3329999.",
        "[17] Apache Software Foundation, \"Apache Parquet Format Specification: Columnar Storage for Hadoop and Big Data Ecosystems,\" 2023. [Online]. Available: https://parquet.apache.org/",
        "[18] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion, O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg, J. Vanderplas, A. Passos, D. Cournapeau, M. Brucher, M. Perrot, and É. Duchesnay, \"Scikit-learn: Machine Learning in Python,\" Journal of Machine Learning Research, vol. 12, pp. 2825–2830, 2011.",
        "[19] dbt Labs, \"dbt (data build tool) Documentation & Analytics Engineering Best Practices,\" 2024. [Online]. Available: https://docs.getdbt.com/",
        "[20] Snowflake Inc., \"Streamlit Documentation: The fastest way to build and share data apps,\" 2024. [Online]. Available: https://docs.streamlit.io/",
        "[21] MinIO Inc., \"MinIO High Performance Object Storage for AI & Data Lake Architectures Documentation,\" 2024. [Online]. Available: https://min.io/docs/"
    ]

    for ref in references_list:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.25
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Pt(24)
        p_ref.paragraph_format.first_line_indent = Pt(-24)
        r_ref = p_ref.add_run(ref)
        r_ref.font.name = "Times New Roman"
        r_ref.font.size = Pt(11)
