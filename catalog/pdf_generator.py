from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import os

# 設定字體與大小
FONT_NAME = "Helvetica-Bold"   # 產品名稱字體
FONT_SIZE_NAME = 14            # 產品名稱字體大小
FONT_DESCRIPTION = "Helvetica" # 產品描述字體
FONT_SIZE_DESCRIPTION = 10     # 產品描述字體大小
FONT_PAGE_NUMBER = "Helvetica" # 頁碼字體
FONT_SIZE_PAGE_NUMBER = 10     # 頁碼字體大小

# 設定圖片最大尺寸
IMAGE_MAX_WIDTH = 150          # 圖片最大寬度
IMAGE_MAX_HEIGHT = 150         # 圖片最大高度

# 出血區設定（3mm = 8.5pt）
BLEED = 8.5  # 出血範圍 (左右上下各 3mm)
PAGE_WIDTH, PAGE_HEIGHT = letter  # Letter 尺寸 (612 x 792 pt)
PAGE_WIDTH += 2 * BLEED  # 擴展 PDF 以包含出血
PAGE_HEIGHT += 2 * BLEED


def draw_bleed_guides(c):
    """
    在 PDF 上繪製出血範圍的虛線矩形，以便檢視印刷區域。
    """
    c.setStrokeColor(colors.red)  # 設定線條顏色（紅色）
    c.setDash(3, 3)  # 設定虛線樣式 (3pt 線條, 3pt 間距)

    # 出血框範圍（比標準頁面尺寸多 8.5pt 出血區）
    c.rect(BLEED, BLEED, PAGE_WIDTH - 2 * BLEED, PAGE_HEIGHT - 2 * BLEED, stroke=1, fill=0)

    # 重置線條樣式
    c.setDash()  # 取消虛線
    c.setStrokeColor(colors.black)  # 重設為黑色


def draw_page_number(c, page_number):
    """
    在 PDF 底部中央添加頁碼（不超出安全範圍）。
    """
    c.setFont(FONT_PAGE_NUMBER, FONT_SIZE_PAGE_NUMBER)
    c.drawCentredString(PAGE_WIDTH / 2, BLEED + 10, f"{page_number}")


def draw_product_background(c, x_position, y_position, item_width, item_height):
    """
    在每個產品區塊後方添加背景，並讓背景稍微縮小，使其不完全填滿區域。
    """
    padding = 10  # 設定背景縮小的邊界（左右上下各縮小 10pt）

    c.setFillColor(colors.lightgrey)
    c.rect(
        x_position + padding,  # X 軸偏移
        y_position - item_height + padding,  # Y 軸偏移
        item_width - 2 * padding,  # 寬度減少
        item_height - 2 * padding,  # 高度減少
        fill=1
    )
    c.setFillColor(colors.black)  # 重設顏色


def draw_product_text(c, x_position, name_y, desc_y, product_name, description):
    """
    繪製產品名稱和描述
    """
    # 產品名稱
    c.setFont(FONT_NAME, FONT_SIZE_NAME)
    c.drawCentredString(x_position, name_y, product_name)

    # 產品描述
    c.setFont(FONT_DESCRIPTION, FONT_SIZE_DESCRIPTION)
    c.setFillColor(colors.gray)
    c.drawCentredString(x_position, desc_y, description)
    c.setFillColor(colors.black)


def draw_page_label(c, page_number):
    """
    在偶數頁的左側與奇數頁的右側添加標籤（矩形），固定在頁面上方。
    """
    label_width = 20  # 標籤寬度
    label_height = 100  # 標籤高度
    margin = BLEED  # 確保不影響出血區域

    c.setFillColor(colors.darkgray)

    if page_number % 2 == 0:  # 偶數頁 (左側)
        x_position = margin
    else:  # 奇數頁 (右側)
        x_position = PAGE_WIDTH - label_width - margin

    y_position = PAGE_HEIGHT - label_height - BLEED
    c.rect(x_position, y_position, label_width, label_height, fill=1)
    c.setFillColor(colors.black)


def generate_pdf(data, output_file="output.pdf"):
    """
    產生 PDF，包含出血區域，並繪製出血範圍的虛線指示框。
    """
    c = Canvas(output_file, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    cols = 2  # 2 欄
    rows = 3  # 3 行
    item_width = (PAGE_WIDTH - 2 * BLEED) / cols
    item_height = (PAGE_HEIGHT - 2 * BLEED) / rows

    count = 0
    page_number = 1

    for index, row in data.iterrows():
        # 當每頁的第一個產品時，繪製出血範圍的虛線框
        if count % (cols * rows) == 0:
            draw_bleed_guides(c)

        col_idx = count % cols
        row_idx = (count // cols) % rows

        x_position = BLEED + col_idx * item_width
        y_position = PAGE_HEIGHT - BLEED - (row_idx + 1) * item_height + 260

        draw_product_background(c, x_position, y_position, item_width, item_height)

        # 插入圖片，確保不影響出血範圍
        img_x = x_position + (item_width - IMAGE_MAX_WIDTH) / 2
        img_y = y_position - IMAGE_MAX_HEIGHT - 15
        try:
            img = ImageReader(row["Image Path"])
            img_width, img_height = img.getSize()
            scale_factor = min(IMAGE_MAX_WIDTH / img_width, IMAGE_MAX_HEIGHT / img_height, 1)
            scaled_width = img_width * scale_factor
            scaled_height = img_height * scale_factor
            c.drawImage(img, img_x, img_y, width=scaled_width, height=scaled_height, preserveAspectRatio=True)
        except Exception as e:
            print(f"Error loading image {row['Image Path']}: {e}")
            c.drawString(img_x, img_y, "Image not available")

        # 繪製產品名稱與描述
        name_y = img_y - 20
        desc_y = name_y - 15
        draw_product_text(c, x_position + item_width / 2, name_y, desc_y, row['Product Name'], row['Description'])

        count += 1

        # 換頁時加入頁碼 & 出血區標籤
        if count % (cols * rows) == 0:
            draw_page_number(c, page_number)
            draw_page_label(c, page_number)
            c.showPage()
            page_number += 1

    # 如果最後一頁未滿 6 項，仍需添加頁碼與標籤
    if count % (cols * rows) != 0:
        draw_page_number(c, page_number)
        draw_page_label(c, page_number)

    c.save()