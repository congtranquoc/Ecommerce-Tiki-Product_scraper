# Tiki.vn Web Scraping and Data Processing
Repository này chứa mã Python để crawl dữ liệu từ trang web Tiki.vn, xử lý thông tin trích xuất, và lưu trữ trong cơ sở dữ liệu MongoDB và MySQL. Ngoài ra, nó cũng bao gồm các chức năng bổ sung như sao lưu dữ liệu, thống kê, và trích xuất thành phần.

## Yêu cầu
1. Python 3.x
2. MongoDB
3. MySQL

# Tác vụ

1. Lấy toàn bộ sản phẩm đang hiển thị trên các danh mục của website tiki.vn. Dữ liệu lấy về sẽ lưu trong MongoDB
2. Trích xuất các trường thông tin sau và lưu vào MySQL để cho team khác sử dụng:
    1. Product name: Tên sản phẩm 
    2. Short description: Mô tả ngắn của sản phẩm
    3. Description: Mô tả chi tiết sản phẩm. Yêu cầu: **clean dữ liệu, lọc bỏ những tag html thừa trong mô tả**
    4. URL: Link sản phẩm
    5. Rating: Đánh giá trung bình về sản phẩm
    6. Số lượng bán
    7. Giá sản phẩm
    8. Category ID: ID của danh mục sản phẩm
    9. day_ago_create
3.. Thống kê:
    1. Mỗi category (bao gồm cả sub-category) có bao nhiêu sản phẩm
    2. Tạo biểu đồ thống kê xuất xứ của các sản phẩm. Ví dụ từ biểu đồ có thể biết: Có bao nhiêu sản phẩm xuất xứ từ Trung Quốc. Từ đó so sánh tỉ lệ xuất xứ của các sản phẩm
    3. Top 10 sản phẩm được bán nhiều nhất, có rating cao nhất và giá thấp nhất
4. Lấy tất cả sản phẩm mà có thông tin “thành phần” trong mô tả. Lưu các thông tin dưới dạng CSV: product_id, ingredient.
