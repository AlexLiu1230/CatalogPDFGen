from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

FONT_NAME = "Helvetica-Bold"   # 產品名稱字體
FONT_SIZE_NAME = 14            # 產品名稱字體大小
FONT_DESCRIPTION = "Helvetica" # 產品描述字體
FONT_SIZE_DESCRIPTION = 10     # 產品描述字體大小
FONT_PAGE_NUMBER = "Helvetica" # 頁碼字體
FONT_SIZE_PAGE_NUMBER = 10     # 頁碼字體大小
IMAGE_MAX_WIDTH = 150          # 圖片最大寬度
IMAGE_MAX_HEIGHT = 150         # 圖片最大高度

def draw_page_number(c, page_number, width):
    """
    在 PDF 底部中央添加頁碼。
    :param c: Canvas 物件。
    :param page_number: 當前頁碼。
    :param width: PDF 的寬度，用於計算置中位置。
    """
    c.setFont(FONT_PAGE_NUMBER, FONT_SIZE_PAGE_NUMBER)
    c.drawCentredString(width / 2, 3, f"{page_number}")

def draw_product_background(c, x_position, y_position, item_width, item_height):
    """
    在每個產品區塊後方添加背景
    :param c: Canvas 物件
    :param x_position: 區塊的 X 座標
    :param y_position: 區塊的 Y 座標
    :param item_width: 區塊寬度
    :param item_height: 區塊高度
    """
    c.setFillColor(colors.lightgrey)  # 設定背景顏色
    c.rect(x_position + 10, y_position - item_height + 20, item_width - 20, item_height - 30, fill=1)
    c.setFillColor(colors.black)  # 重設顏色

def draw_product_text(c, x_position, name_y, desc_y, product_name, description):
    """
    繪製產品名稱和描述
    :param c: Canvas 物件
    :param x_position: 文字的 X 座標
    :param name_y: 名稱的 Y 座標
    :param desc_y: 描述的 Y 座標
    :param product_name: 名稱
    :param description: 描述
    """
    # 產品名稱
    c.setFont(FONT_NAME, FONT_SIZE_NAME) # 粗體，字體大小14
    c.drawCentredString(x_position, name_y, product_name) # 置中

    # 產品描述
    c.setFont(FONT_DESCRIPTION, FONT_SIZE_DESCRIPTION) # 正常，字體大小10
    c.setFillColor(colors.gray) # 灰色
    c.drawCentredString(x_position, desc_y, description) # 置中
    c.setFillColor(colors.black) # 重置為黑色

def generate_pdf(data, output_file="output.pdf"):
    """
    根據給定的 DataFrame 產生產品型錄 PDF。
    :param data: 包含產品資訊的 DataFrame。
    :param output_file: 產出的 PDF 檔案名稱，預設"output.pdf"。
    """
    c = Canvas(output_file, pagesize=letter)
    width, height = letter

    cols = 2  # 每頁 2 欄
    rows = 3  # 每頁 3 行
    item_width = width / cols
    item_height = height / rows

    max_img_width, max_img_height = IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT # 圖片最大尺寸

    count = 0
    for index, row in data.iterrows():
        col_idx = count % cols
        row_idx = (count // cols) % rows

        x_position = col_idx * item_width
        y_position = height - (row_idx + 1) * item_height + 260

        draw_product_background(c, x_position, y_position, item_width, item_height)  # 呼叫美工函數

        # 插入產品圖片
        img_x = x_position + (item_width - max_img_width) / 2 # 水平置中
        img_y = y_position - max_img_height - 15 # 調整垂直位置
        try:
            img = ImageReader(row["Image Path"])
            img_width, img_height = img.getSize()
            scale_factor = min(max_img_width / img_width, max_img_height / img_height, 1) # 只縮小，不放大
            scaled_width = img_width * scale_factor
            scaled_height = img_height * scale_factor
            c.drawImage(img, img_x + (max_img_width - scaled_width) / 2, img_y + (max_img_height - scaled_height) / 2,
                        width=scaled_width, height=scaled_height, preserveAspectRatio=True, anchor='c')
        except Exception as e:
            print(f"Error loading image {row['Image Path']}: {e}")
            c.drawString(img_x, img_y, "Image not available")

        # 文字位置
        name_y = img_y - 20
        desc_y = name_y - 15
        draw_product_text(c, x_position + item_width / 2, name_y, desc_y, row['Product Name'], row['Description'])

        count += 1 # 計算商品數量

        # 每 6 項產品換頁，並添加頁碼
        if count % (cols * rows) == 0:
            draw_page_number(c, count // (cols * rows), width)
            c.showPage()

    # 如果最後一頁未滿 6 項，仍需添加頁碼
    if count % (cols * rows) != 0:
        draw_page_number(c, (count // (cols * rows)) + 1, width)

    c.save()