"""
chapter2.py: Triển khai nội dung CHƯƠNG 2 - CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ NỀN TẢNG.
Bám sát khung tri thức Samsung Innovation Campus Big Data (DataChapter.pdf) và các công trình kinh điển.
Tuân thủ quy chuẩn:
- Không lạm dụng dấu ngoặc đơn ()
- Trích dẫn chuẩn IEEE [X]
- Độ sâu học thuật, phân tích luồng dữ liệu, cơ chế bên dưới, so sánh ưu nhược điểm.
"""

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_generator.styles import (
    add_paragraph, add_heading_1, add_heading_2, add_heading_3,
    add_caption, add_formula_block, add_styled_table
)


def build_chapter_2(doc):
    """Xây dựng toàn bộ nội dung Chương 2."""
    add_heading_1(doc, "CHƯƠNG 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ NỀN TẢNG")

    add_paragraph(doc,
        "Chương 2 trình bày có hệ thống khung lý thuyết khoa học và các công nghệ nền tảng tạo nên sức mạnh của hệ thống. Nội dung bao quát toàn diện từ bài toán xử lý ngôn ngữ tự nhiên, kỹ thuật biểu diễn không gian vectơ và thuật toán học máy phân loại cảm xúc, cho đến các nguyên lý kiến trúc dữ liệu lớn phân tán gồm Apache Spark, mô hình Medallion Lakehouse, định dạng lưu trữ cột Parquet, hệ thống lưu trữ đối tượng MinIO, công cụ chuyển đổi dữ liệu dbt, công cụ truy vấn phân tích DuckDB, lý thuyết kiểm soát quá trình bằng thống kê và nền tảng trực quan hóa Streamlit [6], [7], [8]."
    )

    # 2.1. Xử lý ngôn ngữ tự nhiên và phân tích cảm xúc
    add_heading_2(doc, "2.1. Xử lý ngôn ngữ tự nhiên và phân tích cảm xúc")

    add_heading_3(doc, "2.1.1. Tổng quan về bài toán phân tích cảm xúc")
    add_paragraph(doc,
        "Phân tích cảm xúc văn bản, còn được biết đến với tên gọi khai phá quan điểm, là một phân ngành trọng yếu của xử lý ngôn ngữ tự nhiên và trí tuệ nhân tạo, tập trung vào việc tự động nhận diện, trích xuất và định lượng trạng thái chủ quan của con người từ các dữ liệu văn bản phi cấu trúc [13]. Trong bối cảnh thương mại điện tử, bài toán này nhằm mục đích chuyển hóa các dòng nhận xét phức tạp của người mua sắm thành các tín hiệu định lượng có thể đo lường và lập biểu đồ theo dõi."
    )

    add_paragraph(doc,
        "Về mặt bản chất toán học, bài toán phân tích cảm xúc được mô hình hóa như một bài toán phân loại mẫu có giám sát. Cho một tập hợp các văn bản đánh giá d thuộc không gian tài liệu D, mục tiêu là tìm kiếm một hàm ánh xạ f: D -> C, trong đó C là không gian các nhãn cảm xúc rời rạc. Trong nghiên cứu này, không gian nhãn được định nghĩa gồm ba lớp chuẩn mực là Tích cực, biểu thị mức độ hài lòng cao; Tiêu cực, biểu thị sự thất vọng hoặc khiếu nại về chất lượng; và Trung tính, phản ánh trạng thái lưỡng lự hoặc cảm xúc dung hòa giữa ưu điểm và khuyết điểm của sản phẩm [9]."
    )

    add_paragraph(doc,
        "Thách thức căn bản của phân tích cảm xúc đánh giá hàng hóa trực tuyến nằm ở tính mơ hồ của ngữ nghĩa, sự xuất hiện thường xuyên của các hiện tượng châm biếm, mỉa mai, và đặc biệt là sự chi phối mạnh mẽ của các cấu trúc phủ định. Một sự thay đổi nhỏ trong vị trí của từ ngữ mang tính phủ định có thể đảo ngược hoàn toàn cực tính của toàn bộ câu văn, đòi hỏi các mô hình biểu diễn phải vượt ra khỏi giả định độc lập từ đơn lẻ truyền thống."
    )

    add_heading_3(doc, "2.1.2. Kỹ thuật tiền xử lý văn bản")
    add_paragraph(doc,
        "Dữ liệu văn bản thô thu thập từ môi trường mạng luôn chứa đựng lượng lớn nhiễu cú pháp và các thành phần không mang giá trị biểu đạt cảm xúc. Do đó, quy trình tiền xử lý đóng vai trò là bộ lọc đầu tiên nhằm chuẩn hóa dữ liệu đầu vào và giảm thiểu số chiều của không gian từ vựng [13]. Quy trình này bao gồm các bước tuần tự được thiết kế tối ưu cho dữ liệu thương mại điện tử:"
    )

    add_paragraph(doc,
        "Đầu tiên là bước chuẩn hóa chữ thường. Toàn bộ các ký tự trong câu văn được chuyển về dạng chữ thường thống nhất, giúp hệ thống đồng nhất các biến thể từ ngữ xuất hiện ở đầu câu hoặc do thói quen gõ phím hoa ngẫu nhiên của người dùng, qua đó tránh việc tạo ra hai chiều đặc trưng phân biệt cho cùng một thực thể từ vựng."
    )

    add_paragraph(doc,
        "Tiếp theo là kỹ thuật làm sạch dựa trên biểu thức chính quy. Hệ thống thực hiện bóc tách và loại bỏ hoàn toàn các thẻ định dạng HTML, các liên kết đường dẫn mạng, các ký tự điều khiển ngắt dòng đặc biệt và toàn bộ chuỗi số hoặc ký tự dấu câu không mang thông tin phân loại. Các chuỗi khoảng trắng thừa xuất hiện liên tiếp cũng được rút gọn thành một khoảng trắng chuẩn mực đơn lẻ."
    )

    add_paragraph(doc,
        "Sau đó, văn bản được phân tách thành chuỗi các đơn vị từ ngữ thông qua thao tác tách từ. Các từ dừng vô nghĩa như mạo từ, giới từ có tần suất xuất hiện dày đặc nhưng hoàn toàn vô hại về mặt sắc thái cảm xúc sẽ được loại bỏ chọn lọc. Tuy nhiên, một nguyên tắc thiết kế tối quan trọng trong hệ thống này là tuyệt đối bảo lưu các từ mang ý nghĩa phủ định như not, never, no, barely, bởi việc loại bỏ những từ này sẽ làm phá vỡ ngữ cảnh và biến đổi các nhận xét chỉ trích thành lời khen ngợi giả mạo."
    )

    add_heading_3(doc, "2.1.3. Kỹ thuật biểu diễn văn bản: TF-IDF và N-grams")
    add_paragraph(doc,
        "Máy tính và các thuật toán học máy chỉ có khả năng làm việc với các ma trận số học. Vì vậy, bước chuyển đổi văn bản sang không gian vectơ đóng vai trò quyết định đến độ chính xác của toàn bộ đường ống xử lý. Phương pháp trọng số TF-IDF là một trong những chuẩn mực kinh điển và hiệu quả nhất trong lý thuyết thu hồi thông tin, cho phép lượng hóa tầm quan trọng của từng từ ngữ đối với một văn bản cụ thể trong tương quan với toàn bộ kho ngữ liệu [13]."
    )

    add_paragraph(doc,
        "Trọng số TF-IDF của một từ ngữ t trong văn bản d thuộc tập tài liệu D được xác định bằng tích của hai thành phần toán học độc lập:"
    )

    add_formula_block(doc, "TF-IDF(t, d, D) = TF(t, d) * IDF(t, D)", "Công thức 2.1")

    add_paragraph(doc,
        "Trong đó, thành phần tần suất từ TF(t, d) phản ánh mức độ xuất hiện của từ t ngay trong bản đánh giá d. Để tránh việc các bài đánh giá dài có số lần lặp từ áp đảo các bài đánh giá ngắn, tần suất này thường được chuẩn hóa tuyến tính dưới dạng tỷ lệ giữa số lần từ t xuất hiện trên tổng số từ của văn bản d. Thành phần thứ hai là nghịch đảo tần suất văn bản IDF(t, D), có tác dụng triệt tiêu ảnh hưởng của các từ ngữ xuất hiện quá phổ biến ở mọi nơi và nâng cao trọng số của các từ ngữ hiếm mang tính đặc trưng cao, được tính theo thang đo logarit:"
    )

    add_formula_block(doc, "IDF(t, D) = log( (1 + |D|) / (1 + DF(t, D)) ) + 1", "Công thức 2.2")

    add_paragraph(doc,
        "với |D| là tổng số lượng bài đánh giá trong kho ngữ liệu và DF(t, D) là số lượng bài đánh giá có chứa từ t. Tuy nhiên, nếu chỉ sử dụng mô hình từ đơn Unigram, hệ thống sẽ hoàn toàn bất lực trong việc nhận biết các cụm từ ngữ mang nghĩa đảo ngược do giả định túi từ xem các từ ngữ là hoàn toàn độc lập với nhau. Để khắc phục triệt để hạn chế này, nghiên cứu tích hợp kỹ thuật mở rộng N-gram bậc hai, tức Bigram. Bằng cách trích xuất cả các cặp từ xuất hiện liền kề nhau như not good, totally waste, never buy, mô hình bảo toàn được trọn vẹn ngữ cảnh ngữ pháp cục bộ mà vẫn duy trì được tính toán thưa thớt, không làm gia tăng chi phí bộ nhớ như các mạng nơ-ron hồi quy phức tạp [9]."
    )

    add_heading_3(doc, "2.1.4. Thuật toán phân loại học máy: Linear SVM và Hồi quy Logistic")
    add_paragraph(doc,
        "Trong không gian biểu diễn văn bản bằng TF-IDF và N-gram, số chiều của không gian đặc trưng có thể lên tới hàng trăm nghìn chiều nhưng ma trận dữ liệu lại có độ thưa rất cao, bởi mỗi bài đánh giá chỉ chứa một tỷ lệ từ vựng rất nhỏ trong toàn bộ kho từ điển. Đối với loại dữ liệu đặc thù này, thuật toán Máy vectơ hỗ trợ tuyến tính, tức Linear SVM, được chứng minh là lựa chọn tối ưu vượt bậc về cả độ chính xác toán học lẫn tốc độ tính toán [9]."
    )

    add_paragraph(doc,
        "Nguyên lý vận hành cốt lõi của Linear SVM bắt nguồn từ lý thuyết học thống kê của Vapnik, hướng tới việc tìm kiếm một siêu phẳng phân tách tuyến tính w^T * x + b = 0 sao cho khoảng cách biên giữa các lớp dữ liệu phân loại đạt giá trị cực đại, được gọi là nguyên tắc biên cực đại. Khoảng cách biên hình học được xác định bằng 2 / ||w||, do đó bài toán huấn luyện được phát biểu dưới dạng bài toán tối ưu hóa lồi có ràng buộc:"
    )

    add_formula_block(doc, "Tối thiểu hóa:  (1/2) * ||w||^2 + C * Tổng( Xi_i )", "Công thức 2.3")

    add_formula_block(doc, "với điều kiện:  y_i * ( w^T * x_i + b ) >= 1 - Xi_i,  Xi_i >= 0", "Công thức 2.4")

    add_paragraph(doc,
        "trong đó y_i là nhãn thực tế, Xi_i là biến nới lỏng cho phép một số điểm dữ liệu vi phạm biên trong trường hợp dữ liệu không tách biệt tuyến tính hoàn toàn, và tham số C điều chỉnh sự cân bằng giữa độ rộng của biên và mức độ chấp nhận lỗi phân loại. Điểm ưu việt căn bản của Linear SVM so với mô hình Hồi quy Logistic là hàm mất mát dạng bản lề Hinge Loss chỉ phụ thuộc duy nhất vào các điểm dữ liệu nằm sát biên giới hạn, được gọi là các vectơ hỗ trợ, chứ không bị phân tán bởi toàn bộ các điểm nằm sâu bên trong lớp, giúp mô hình có khả năng chống hiện tượng quá khớp cực kỳ xuất sắc trong không gian nhiều chiều [9]."
    )

    add_paragraph(doc,
        "Để giải quyết bài toán đa lớp gồm ba trạng thái Tích cực, Trung tính và Tiêu cực, kiến trúc One-vs-Rest được áp dụng. Phương pháp này huấn luyện ba bộ phân loại nhị phân độc lập, mỗi bộ phân loại chịu trách nhiệm phân biệt một lớp cụ thể với hai lớp còn lại. Quyết định phân loại cuối cùng cho một mẫu văn bản mới được đưa ra bằng cách tính giá trị khoảng cách ký số tới siêu phẳng qua hàm quyết định decision_function và lựa chọn lớp có giá trị khoảng cách lớn nhất."
    )

    add_heading_3(doc, "2.1.5. Kỹ thuật giải quyết mất cân bằng nhãn")
    add_paragraph(doc,
        "Hiện tượng mất cân bằng dữ liệu đặt ra một thách thức nghiêm trọng đối với hàm tối ưu hóa chuẩn tắc. Khi số lượng mẫu lớp Tích cực áp đảo lớp Trung tính và Tiêu cực với tỷ lệ xấp xỉ bảy trên một, thuật toán học máy có xu hướng tối thiểu hóa hàm mất mát toàn cục bằng cách dự đoán hầu hết các mẫu về lớp đa số, dẫn đến việc độ chính xác tổng thể có thể rất cao nhưng độ nhạy và chỉ số F1 của các lớp thiểu số lại rơi xuống mức tiệm cận không. Trong nghiên cứu này, hai chiến lược giải quyết bất đối xứng được đưa vào thực nghiệm đối sánh chuyên sâu [12]."
    )

    add_paragraph(doc,
        "Chiến lược thứ nhất là kỹ thuật lấy mẫu lại phân tầng có giảm bớt mẫu, tức Stratified Downsampling. Phương pháp này lấy số lượng mẫu của lớp thiểu số nhất làm chuẩn chuẩn hóa, sau đó rút trích ngẫu nhiên các mẫu từ các lớp đa số sao cho số lượng mẫu của ba lớp ở tập huấn luyện trở nên hoàn toàn bằng nhau. Ưu điểm của phương pháp này là giảm mạnh quy mô dữ liệu huấn luyện, rút ngắn thời gian tính toán nhưng phải đánh đổi bằng tổn thất thông tin rất lớn do phải loại bỏ vĩnh viễn hơn một triệu bản ghi dữ liệu hợp lệ."
    )

    add_paragraph(doc,
        "Chiến lược thứ hai là phương pháp gán trọng số nhạy cảm chi phí, tức Class Weighting. Phương pháp này bảo toàn toàn bộ dữ liệu huấn luyện nguyên vẹn, nhưng gán một hệ số phạt W_k tỷ lệ nghịch với tần suất xuất hiện của lớp k trong hàm mục tiêu tối ưu hóa:"
    )

    add_formula_block(doc, "W_k = N / ( K * N_k )", "Công thức 2.5")

    add_paragraph(doc,
        "với N là tổng số mẫu trong tập huấn luyện, K là số lượng lớp phân loại và N_k là số lượng mẫu của lớp k. Khi mô hình phân loại sai một mẫu thuộc lớp thiểu số, mức phạt gánh chịu sẽ lớn gấp nhiều lần so với khi phân loại sai một mẫu thuộc lớp đa số, buộc siêu phẳng phân tách phải dịch chuyển về vị trí công bằng hơn giữa các nhóm nhãn."
    )

    # 2.2. Kiến trúc Big Data và hệ thống tính toán phân tán
    add_heading_2(doc, "2.2. Kiến trúc Big Data và hệ thống tính toán phân tán")

    add_heading_3(doc, "2.2.1. Tổng quan về Apache Spark và cơ chế tính toán trong bộ nhớ")
    add_paragraph(doc,
        "Trong kỷ nguyên dữ liệu lớn ban đầu, mô hình tính toán phân tán MapReduce của hệ sinh thái Hadoop giữ vai trò thống trị. Tuy nhiên, như được phân tích chi tiết trong tài liệu chuyên đề của Samsung Innovation Campus, mô hình MapReduce bộc lộ một điểm nghẽn hiệu năng nghiêm trọng là phụ thuộc hoàn toàn vào các thao tác đọc và ghi đĩa cứng HDFS giữa mỗi chu kỳ xử lý [6], [14]. Mỗi giai đoạn chuyển tiếp dữ liệu đòi hỏi chi phí I/O đĩa cục bộ vô cùng đắt đỏ, khiến các thuật toán học máy có tính chất lặp đi lặp lại nhiều vòng hoặc các truy vấn phân tích tương tác chịu độ trễ cực lớn."
    )

    add_paragraph(doc,
        "Sự xuất hiện của Apache Spark vào năm 2010 đã tạo nên bước ngoặt cách mạng khi chi phí bộ nhớ RAM toàn cầu giảm mạnh, cho phép chuyển dịch toàn bộ mô hình sang tính toán phân tán ngay trên bộ nhớ trong [7]. Spark chỉ phát sinh chi phí I/O khi tải dữ liệu ban đầu và ghi kết quả cuối cùng, trong khi toàn bộ chu kỳ tính toán trung gian được giữ nguyên trên bộ nhớ RAM phân tán của cụm máy chủ, mang lại tốc độ thực thi nhanh gấp từ mười đến một trăm lần so với MapReduce truyền thống. Bảng 2.1 tóm tắt sự khác biệt bản chất giữa hai nền tảng tính toán này."
    )

    add_caption(doc, "Bảng 2.1: So sánh cơ chế tính toán giữa Hadoop MapReduce và Apache Spark", is_table=True)
    headers_t3 = ["Tiêu chí kỹ thuật", "Hadoop MapReduce", "Apache Spark"]
    rows_t3 = [
        ["Vị trí lưu trạng thái trung gian", "Ghi bắt buộc xuống đĩa cứng HDFS cục bộ", "Lưu trữ trực tiếp trên bộ nhớ RAM phân tán"],
        ["Độ trễ xử lý dữ liệu", "Độ trễ cao do nghẽn I/O đĩa và tuần tự hóa", "Độ trễ cực thấp nhờ tính toán in-memory"],
        ["Mô hình lập trình trừu tượng", "Chỉ giới hạn ở hai hàm cứng nhắc Map và Reduce", "Hỗ trợ phong phú hơn 80 toán tử biến đổi dữ liệu"],
        ["Khả năng phục hồi lỗi", "Sao chép dư thừa khối dữ liệu ba bản trên đĩa", "Tái tạo dữ liệu tự động dựa trên đồ thị Lineage DAG"],
        ["Phù hợp thuật toán lặp", "Kém hiệu quả, lặp đi lặp lại việc đọc đĩa", "Tối ưu xuất sắc cho các thuật toán học máy lặp"],
        ["Giao diện truy vấn bậc cao", "Phụ thuộc vào các công cụ bổ trợ như Apache Hive", "Tích hợp sẵn Spark SQL, DataFrame API, MLlib"]
    ]
    add_styled_table(doc, headers_t3, rows_t3, col_widths=[4.5, 5.5, 6.0])

    add_paragraph(doc,
        "Cấu trúc trừu tượng nền tảng của Spark là RDD, viết tắt của Resilient Distributed Dataset, đại diện cho một tập hợp các đối tượng dữ liệu bất biến được phân mảnh trên các nút của cụm máy chủ và có khả năng phục hồi lỗi hoàn hảo [7]. Tính năng đàn hồi này đạt được nhờ cơ chế đồ thị dòng dõi Lineage Graph dưới dạng đồ thị có hướng không chu trình DAG. Spark không sao chép dữ liệu trung gian sang các máy khác để dự phòng mà lưu lại toàn bộ chuỗi biến đổi toán học đã tạo ra RDD đó. Khi một phân vùng dữ liệu trên một nút bị lỗi bộ nhớ, Spark chỉ việc thực thi lại chuỗi toán tử tương ứng từ điểm kiểm tra gần nhất để tái tạo chính xác phân vùng bị mất."
    )

    add_paragraph(doc,
        "Spark vận hành dựa trên cơ chế đánh giá lười biếng. Toàn bộ các toán tử biến đổi dữ liệu như map, filter, select không sinh ra kết quả tính toán ngay lập tức mà chỉ ghi nhận vào đồ thị DAG. Quá trình tính toán thực sự chỉ được kích hoạt khi một toán tử hành động như count, collect hoặc write được gọi. Kiến trúc phân tán của Spark tuân thủ mô hình chủ tớ kinh điển, trong đó chương trình Driver đóng vai trò điều phối trung tâm, phân chia công việc thành các giai đoạn và tác vụ, sau đó gửi tới các tiến trình Executor chạy trên các nút công nhân để thực thi song song [8]."
    )

    add_heading_3(doc, "2.2.2. PySpark MLlib và Tối ưu hóa Catalyst")
    add_paragraph(doc,
        "Mặc dù RDD cung cấp quyền kiểm soát cấp thấp mạnh mẽ, lập trình với dữ liệu có cấu trúc đòi hỏi một giao diện cấp cao hơn. Spark SQL và DataFrame API ra đời nhằm cung cấp mô hình bảng biểu tương tự như cơ sở dữ liệu quan hệ nhưng có khả năng mở rộng phân tán trên hàng triệu dòng dữ liệu. Trung tâm sức mạnh của Spark SQL là trình tối ưu hóa truy vấn thông minh mang tên Catalyst Optimizer [15]."
    )

    add_paragraph(doc,
        "Trình tối ưu hóa Catalyst xử lý các truy vấn DataFrame qua bốn giai đoạn tuần tự khép kín: phân tích cú pháp để ánh xạ các cột dữ liệu với bảng danh mục catalog; tối ưu hóa logic bằng cách áp dụng các quy tắc như đẩy vị từ lọc xuống sớm nhất có thể và cắt tỉa các cột không sử dụng; lập kế hoạch vật lý để lựa chọn giải thuật thực thi tối ưu dựa trên mô hình chi phí; và cuối cùng là sinh mã bytecode Java trực tiếp ngay khi thực thi thông qua công nghệ Tungsten [6]. Nhờ cơ chế này, các đoạn mã viết bằng cú pháp SQL thuần túy hay phương thức DataFrame đều đạt được hiệu năng ngang bằng nhau, độc lập với ngôn ngữ lập trình phía người dùng."
    )

    add_heading_3(doc, "2.2.3. Kiến trúc Medallion Lakehouse")
    add_paragraph(doc,
        "Theo bài giảng chuyên sâu về kiến trúc dữ liệu của Samsung Innovation Campus, các tổ chức truyền thống thường phải đối mặt với sự đánh đổi nghiệt ngã giữa Kho dữ liệu doanh nghiệp và Hồ dữ liệu [6]. Kho dữ liệu có ưu điểm là tốc độ truy vấn nhanh, hỗ trợ đầy đủ các giao dịch nhất quán ACID và kiểm soát chất lượng chặt chẽ nhưng lại có nhược điểm chí mạng là chi phí phần cứng đắt đỏ, lược đồ cấu trúc cứng nhắc và không thể lưu trữ các dạng dữ liệu văn bản phi cấu trúc. Ngược lại, Hồ dữ liệu cho phép lưu trữ mọi định dạng thô với chi phí cực rẻ trên nền tảng lưu trữ đối tượng nhưng lại thiếu vắng cơ chế quản trị, không có giao dịch ACID, dẫn đến nguy cơ biến thành một đầm lầy dữ liệu hỗn loạn và không đáng tin cậy [11]."
    )

    add_paragraph(doc,
        "Kiến trúc Lakehouse ra đời nhằm xóa bỏ hoàn toàn sự đánh đổi này bằng cách kết hợp tính linh hoạt và chi phí thấp của hệ thống lưu trữ đối tượng với khả năng quản trị và độ tin cậy giao dịch của kho dữ liệu. Mô hình Medallion là hiện thân tiêu biểu của Lakehouse, tổ chức luồng luân chuyển dữ liệu qua ba tầng tinh chế liên tục [6], [11]:"
    )

    add_paragraph(doc,
        "Tầng Đồng là tầng tiếp nhận nguyên bản toàn bộ dữ liệu thô từ các nguồn phân tán mà không qua bất kỳ biến đổi ngữ nghĩa nào. Dữ liệu được ghi nhận theo nguyên tắc nạp nguyên trạng, bảo toàn mọi thuộc tính ban đầu nhằm phục vụ công tác kiểm toán và sẵn sàng tái tạo lại toàn bộ hệ thống nếu phát sinh lỗi xử lý ở các tầng sau."
    )

    add_paragraph(doc,
        "Tầng Bạc là tầng dữ liệu đã qua làm sạch, chuẩn hóa kiểu dữ liệu, khử trùng lặp và loại bỏ các dị biệt cấu trúc. Đây là tầng cung cấp một nguồn sự thật duy nhất và đáng tin cậy về mặt cấu trúc, tối ưu hóa cho các kỹ sư dữ liệu và các nhà khoa học dữ liệu tiến hành trích xuất đặc trưng phục vụ huấn luyện mô hình học máy."
    )

    add_paragraph(doc,
        "Tầng Vàng là tầng dữ liệu nghiệp vụ cao nhất, lưu trữ các bảng dữ liệu tổng hợp, các chỉ số đo lường hiệu năng then chốt và các kết quả suy luận từ mô hình trí tuệ nhân tạo. Dữ liệu tại tầng Vàng được thiết kế dạng lược đồ hình sao hoặc bảng dữ liệu thực tế, tối ưu hóa cho các truy vấn phân tích nghiệp vụ, báo cáo quản trị và các hệ thống cảnh báo tự động."
    )

    add_heading_3(doc, "2.2.4. Định dạng lưu trữ Parquet và Phân vùng Partitioning")
    add_paragraph(doc,
        "Tại các tầng Bạc và Vàng, định dạng dữ liệu cột Apache Parquet được lựa chọn làm tiêu chuẩn lưu trữ duy nhất. Khác với các định dạng hướng dòng truyền thống như CSV hay JSON vốn bắt buộc phải đọc tuần tự toàn bộ các trường thông tin của một dòng dữ liệu, định dạng hướng cột Parquet gom nhóm các giá trị của cùng một cột nằm liền kề nhau trên đĩa từ [17]."
    )

    add_paragraph(doc,
        "Cấu trúc tệp Parquet bao gồm ba cấp độ tổ chức chặt chẽ: Siêu dữ liệu tệp lưu trữ ở cuối tệp chứa sơ đồ lược đồ và vị trí các khối; các nhóm dòng là sự phân chia ngang của dữ liệu; và các đoạn cột chứa dữ liệu của một cột duy nhất trong nhóm dòng đó. Thiết kế này mang lại hai lợi thế đột phá về hiệu năng tính toán:"
    )

    add_paragraph(doc,
        "Thứ nhất là khả năng nén dữ liệu phi thường. Do các giá trị trong cùng một cột có cùng kiểu dữ liệu và thường có tính lặp lại cao, Parquet áp dụng kết hợp thuật toán mã hóa từ điển, mã hóa độ dài loạt và thuật toán nén Snappy, giúp giảm kích thước tệp lưu trữ trên đĩa tới hơn 70% so với dữ liệu JSON thô."
    )

    add_paragraph(doc,
        "Thứ hai là kỹ thuật cắt tỉa dữ liệu thông qua cơ chế đẩy bộ lọc. Siêu dữ liệu của mỗi đoạn cột tự động lưu trữ giá trị nhỏ nhất và lớn nhất của cột đó. Khi câu truy vấn SQL thực hiện lọc theo thời gian hoặc danh mục, công cụ truy vấn có thể bỏ qua hoàn toàn việc đọc hàng trăm gigabyte dữ liệu không thỏa mãn điều kiện lọc từ đĩa, giúp tiết kiệm triệt để tài nguyên I/O và tăng tốc độ truy vấn lên gấp nhiều lần [6]."
    )

    # 2.3. Hạ tầng lưu trữ và điều phối
    add_heading_2(doc, "2.3. Hạ tầng lưu trữ và điều phối")

    add_heading_3(doc, "2.3.1. Hệ thống lưu trữ đối tượng MinIO")
    add_paragraph(doc,
        "MinIO là một hệ thống lưu trữ đối tượng phân tán mã nguồn mở hiệu năng cao, tương thích hoàn toàn với giao diện lập trình ứng dụng Amazon S3 API [6]. Trong kiến trúc của đề tài, MinIO đóng vai trò là xương sống lưu trữ cho toàn bộ hệ thống Data Lakehouse cục bộ. Dữ liệu được tổ chức dưới dạng các thùng chứa độc lập đại diện cho các tầng Đồng, Bạc và Vàng, giao tiếp với cụm Apache Spark thông qua giao thức s3a hiệu năng cao."
    )

    add_heading_3(doc, "2.3.2. Công cụ mô hình hóa dữ liệu dbt và In-Process OLAP DuckDB")
    add_paragraph(doc,
        "Để chuyển đổi dữ liệu từ các bảng sự kiện sang các bảng phục vụ phân tích nghiệp vụ tại tầng Vàng, hệ thống kết hợp bộ đôi công nghệ dbt và DuckDB [10], [16]. dbt là công cụ tiên phong trong ngành kỹ thuật phân tích dữ liệu, cho phép các kỹ sư dữ liệu viết mã chuyển đổi hoàn toàn bằng ngôn ngữ SQL khai báo, tự động quản lý các phụ thuộc giữa các mô hình thông qua biểu đồ DAG và thực thi kiểm thử chất lượng dữ liệu tự động."
    )

    add_paragraph(doc,
        "DuckDB là một hệ quản trị cơ sở dữ liệu phân tích OLAP nhúng hiện đại, được thiết kế chuyên biệt để thực thi các truy vấn phân tích phức tạp ngay bên trong tiến trình của ứng dụng [16]. Với động cơ thực thi véc-tơ hóa theo cột, DuckDB có khả năng xử lý hàng triệu bản ghi trực tiếp từ các tệp Parquet mà không cần thông qua máy chủ cơ sở dữ liệu trung gian, đạt tốc độ truy vấn dưới một phần nghìn giây và hỗ trợ kiểm soát kết nối chỉ đọc an toàn, loại bỏ hoàn toàn xung đột khóa tệp."
    )

    add_heading_3(doc, "2.3.3. Lý thuyết Kiểm soát chất lượng thống kê: Z-Score và Cửa sổ trượt")
    add_paragraph(doc,
        "Lý thuyết kiểm soát quá trình bằng thống kê do Walter Shewhart khởi xướng là nền tảng toán học kinh điển được áp dụng rộng rãi trong các ngành công nghiệp sản xuất chính xác nhằm phân biệt giữa các biến thiên ngẫu nhiên thông thường và các biến thiên có nguyên nhân bất thường [10]. Trong đề tài này, nguyên lý SPC được chuyển hóa sáng tạo thành động cơ cảnh báo đột biến lỗi sản phẩm trong thương mại điện tử."
    )

    add_paragraph(doc,
        "Thay vì áp dụng một ngưỡng cứng tĩnh nhắc cho toàn bộ các sản phẩm vốn có quy mô bán hàng rất khác nhau, hệ thống thiết lập đường cơ sở động dựa trên chính lịch sử hoạt động của từng mã sản phẩm cụ thể. Với mỗi sản phẩm trong tháng quan sát m, hệ thống trích xuất tỷ lệ đánh giá tiêu cực của ba tháng liền trước thông qua cửa sổ trượt quá khứ. Giá trị trung bình kỳ vọng mu và độ lệch chuẩn sigma của đường cơ sở được xác định làm chuẩn mực so sánh:"
    )

    add_formula_block(doc, "Z = ( NegRate_m - Mu_baseline ) / Sigma_baseline", "Công thức 2.6")

    add_paragraph(doc,
        "Chỉ số Z-score phản ánh mức độ lệch của tỷ lệ tiêu cực trong tháng hiện tại so với lịch sử tính theo đơn vị độ lệch chuẩn. Theo quy luật phân phối chuẩn, một giá trị Z vượt ngưỡng 2.0 hoặc 3.0 thể hiện xác suất xuất hiện ngẫu nhiên là cực kỳ thấp, báo hiệu chắc chắn rằng sản phẩm đang gặp sự cố kỹ thuật nghiêm trọng hoặc lỗi chất lượng gia công cần có sự can thiệp khẩn cấp từ nhà sản xuất [10]."
    )

    add_heading_3(doc, "2.3.4. Đóng gói hệ thống với Docker và Trực quan hóa Streamlit")
    add_paragraph(doc,
        "Để đảm bảo tính tái lập và đồng nhất môi trường khi triển khai trên các hạ tầng máy chủ khác nhau, toàn bộ các thành phần dịch vụ phụ trợ bao gồm MinIO Object Storage, Spark Master, Spark Worker được đóng gói độc lập thông qua công nghệ Docker và điều phối tập trung bằng Docker Compose. Cách tiếp cận này loại bỏ hoàn toàn các lỗi xung đột phiên bản thư viện và đảm bảo hệ thống có thể khởi tạo nhanh chóng chỉ với một câu lệnh điều khiển duy nhất."
    )

    add_paragraph(doc,
        "Cuối cùng, giao diện trực quan hóa được phát triển trên nền tảng Streamlit, một framework hiện đại cho phép xây dựng ứng dụng web dữ liệu tương tác bằng ngôn ngữ Python thuần túy [11]. Nhờ cơ chế lưu đệm thông minh trong bộ nhớ RAM và thiết kế truy vấn không khóa tệp, Streamlit mang lại khả năng khám phá dữ liệu mượt mà, hỗ trợ người dùng theo dõi biểu đồ xu hướng nhiều chiều và lọc danh sách sản phẩm cảnh báo mà không tạo độ trễ đối với tầng lưu trữ."
    )

    # 2.4. Kết luận chương
    add_heading_2(doc, "2.4. Kết luận chương")
    add_paragraph(doc,
        "Chương 2 đã cung cấp một bức tranh toàn diện và sâu sắc về các cơ sở lý thuyết khoa học và nền tảng công nghệ chi phối toàn bộ hệ thống. Từ các nguyên lý tối ưu biên phân cách của Linear SVM, kỹ thuật N-gram bảo toàn phủ định, cơ chế tính toán trong bộ nhớ RDD của Apache Spark cho đến cấu trúc tinh chế ba tầng của Medallion Lakehouse, định dạng cột Parquet và mô hình thống kê SPC Z-score, toàn bộ các mắt xích kỹ thuật đã được phân tích rành mạch. Đây chính là khung lý thuyết vững vàng để tiến hành thiết kế kiến trúc chi tiết và triển khai thực nghiệm toàn diện trong Chương 3."
    )

    doc.add_page_break()
