import csv
import os
import chardet
from jinja2 import Environment, FileSystemLoader


def generate_pages():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 文件路径
    product_info_csv_path = os.path.join(current_directory, 'product_info.csv')
    single_product_template_path = os.path.join(current_directory,'single_product_template.html')
    summary_page_template_path = os.path.join(current_directory,'summary_page_template.html')
    # 加载模板
    env = Environment(loader=FileSystemLoader(current_directory))
    single_product_template = env.get_template('single_product_template.html')
    summary_page_template = env.get_template('summary_page_template.html')

    try:
        # 检测文件编码
        with open(product_info_csv_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        # 读取CSV数据
        products = []
        with open(product_info_csv_path, 'r', encoding=encoding) as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 直接使用原链接，去掉链接处理逻辑
                row['image_url1_processed'] = row['image_url1']
                row['image_url2_processed'] = row['image_url2']
                products.append(row)
        if not products:
            print("产品数据为空")
            return
        # 创建输出目录
        output_dir = os.path.join(current_directory, 'html_pages')
        os.makedirs(output_dir, exist_ok=True)
        # 生成单产品页
        products_per_page = 100
        for index, product in enumerate(products):
            page_num = (index // products_per_page) + 1
            product_html = single_product_template.render(
                product_name=product.get('product_name', f'Product {index + 1}'),
                image1=product['image_url1_processed'],
                image2=product['image_url2_processed'],
                product_data=product,
                previous_page=f'page_{page_num}.html'
            )
            output_path = os.path.join(output_dir, f'product_{index + 1}.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(product_html)
            product['page_link'] = f'product_{index + 1}.html'

        # 生成汇总页（新增分页计算逻辑）
        products_per_page = 100
        total_products = len(products)
        total_pages = (total_products + products_per_page - 1) // products_per_page

        for page_num in range(total_pages):
            start_index = page_num * products_per_page
            end_index = start_index + products_per_page
            page_products = products[start_index:end_index]

            summary_html = summary_page_template.render(
                products=page_products,
                current_page=page_num + 1,
                total_pages=total_pages,
                has_prev=page_num > 0,
                has_next=page_num < total_pages - 1
            )

            output_path = os.path.join(output_dir, f'page_{page_num + 1}.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_html)

    except Exception as e:
        import traceback
        print(f"错误: {str(e)}")
        traceback.print_exc()


if __name__ == '__main__':
    generate_pages()