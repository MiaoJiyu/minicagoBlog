#!/usr/bin/env python3
"""
递归遍历当前目录，将所有 Markdown 文件转换为 PDF，输出到 ./export_pdf。
支持自定义字体、页边距、页面大小，通过 CSS 样式提升美观性。
推荐使用 wkhtmltopdf 引擎（简单可靠），也可使用 xelatex。
"""

import os
import sys
import subprocess
import argparse
import tempfile
from pathlib import Path

# 默认 CSS 样式（移除了边距，完全由 --margin 控制）
DEFAULT_CSS = """
/* 全局字体和行距 */
body {
    font-family: 'SimSun', '宋体', 'KaiTi', '楷体', 'Microsoft YaHei', '微软雅黑', serif;
    font-size: 12pt;
    line-height: 1.5;
}

/* 标题样式 */
h1, h2, h3, h4, h5, h6 {
    font-family: inherit;
    margin-top: 1.2em;
    margin-bottom: 0.6em;
}
h1 { font-size: 1.8em; }
h2 { font-size: 1.5em; }
h3 { font-size: 1.2em; }

/* 段落首行缩进 2 字符 */
p {
    text-indent: 2em;
    margin: 0 0 0.8em 0;
}

/* 代码块样式 */
pre, code {
    font-family: 'Courier New', monospace;
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 2px 4px;
}
pre {
    padding: 10px;
    overflow-x: auto;
}

/* 列表样式 */
ul, ol {
    margin: 0.5em 0;
    padding-left: 2em;
}

/* 表格样式 */
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #f2f2f2;
}

/* 图片自适应 */
img {
    max-width: 100%;
    height: auto;
}

/* 引用样式 */
blockquote {
    margin: 0 0 0.8em 0;
    padding-left: 1em;
    border-left: 4px solid #ccc;
    color: #666;
}
"""


def find_markdown_files(root_dir):
    """查找所有 .md / .markdown 文件"""
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith(('.md', '.markdown')):
                full_path = os.path.join(dirpath, fname)
                rel_path = os.path.relpath(full_path, start=root_dir)
                yield full_path, rel_path


def ensure_output_dir(output_base, rel_path):
    """创建输出子目录"""
    out_dir = os.path.join(output_base, os.path.dirname(rel_path))
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    return out_dir


def convert_md_to_pdf(md_path, pdf_path, font, margin, page_size, pdf_engine, extra_args, css_path):
    """使用 pandoc 转换单个 Markdown 文件为 PDF"""
    cmd = [
        'pandoc',
        md_path,
        '-o', pdf_path,
        f'--pdf-engine={pdf_engine}',
        f'--css={css_path}',           # 注入自定义 CSS
        f'-V', f'papersize={page_size}',
        f'-V', f'geometry:margin={margin}',  # 传递给 PDF 引擎的边距（对 wkhtmltopdf 也有效）
    ]

    # 可选：为 xelatex 设置字体（如果用户仍想用）
    if pdf_engine in ('xelatex', 'lualatex'):
        cmd.extend(['-V', f'mainfont={font}'])
        cmd.extend(['-V', f'CJKmainfont={font}'])

    cmd.extend(extra_args)

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        return True, None
    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(cmd)}\nSTDERR:\n{e.stderr}"
        return False, error_msg
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(
        description='将当前目录下所有 Markdown 文件转换为 PDF，保持目录结构。'
    )
    parser.add_argument(
        '--font', default='SimSun',
        help='主字体（仅在 xelatex/lualatex 引擎下有效；wkhtmltopdf 通过 CSS 控制字体）。'
    )
    parser.add_argument(
        '--margin', default='1in',
        help='页边距，例如 "1in" 或 "top=1in,bottom=1in,left=1.5in,right=1.5in"。'
    )
    parser.add_argument(
        '--page-size', default='a4',
        help='纸张大小，例如 a4, letter, 16k。'
    )
    parser.add_argument(
        '--pdf-engine', default='wkhtmltopdf',
        help='PDF 引擎（wkhtmltopdf, xelatex, lualatex 等）。推荐 wkhtmltopdf。'
    )
    parser.add_argument(
        '--output-dir', default='./export_pdf',
        help='输出根目录（默认 ./export_pdf）。'
    )
    parser.add_argument(
        '--style', default=None,
        help='自定义 CSS 文件路径。若不提供，使用内置默认样式。'
    )
    parser.add_argument(
        '--pandoc-args', nargs='*', default=[],
        help='直接传递给 pandoc 的额外参数，例如 --toc。'
    )
    args = parser.parse_args()

    # 检查 pandoc 是否可用
    try:
        subprocess.run(['pandoc', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("错误：未找到 pandoc，请先安装。", file=sys.stderr)
        sys.exit(1)

    # 检查 PDF 引擎是否可用
    try:
        subprocess.run([args.pdf_engine, '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"错误：PDF 引擎 '{args.pdf_engine}' 不可用。", file=sys.stderr)
        if args.pdf_engine == 'wkhtmltopdf':
            print("请从 https://wkhtmltopdf.org/downloads.html 下载安装，并确保 wkhtmltopdf.exe 在 PATH 中。", file=sys.stderr)
        else:
            print(f"请确保 {args.pdf_engine} 已安装并加入 PATH。", file=sys.stderr)
        sys.exit(1)

    # 准备 CSS 文件路径
    if args.style:
        css_path = args.style
        if not os.path.isfile(css_path):
            print(f"错误：CSS 文件 '{css_path}' 不存在。", file=sys.stderr)
            sys.exit(1)
    else:
        # 创建临时 CSS 文件，内容为默认样式（可动态插入用户指定的字体）
        css_content = DEFAULT_CSS
        # 如果用户指定了字体，可以替换 CSS 中的字体族顺序（将用户字体放在最前面）
        if args.font and args.pdf_engine == 'wkhtmltopdf':
            # 将用户字体添加到 CSS 的 font-family 首位
            import re
            # 简单替换：寻找 body 中的 font-family 行，在第一个引号后插入用户字体
            new_family = f"'{args.font}', " + re.search(r"font-family:\s*([^;]+);", css_content).group(1)
            css_content = re.sub(r"font-family:\s*[^;]+;", f"font-family: {new_family};", css_content)

        # 创建临时文件
        tmp_css = tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False, encoding='utf-8')
        tmp_css.write(css_content)
        tmp_css.close()
        css_path = tmp_css.name
        # 注意：程序结束后需要删除临时文件，但为了方便，我们保留，用户可手动删除
        print(f"使用内置 CSS 样式，临时文件保存在: {css_path}")

    root_dir = os.getcwd()
    output_base = os.path.abspath(args.output_dir)
    success_count = 0
    fail_count = 0

    for full_path, rel_path in find_markdown_files(root_dir):
        out_dir = ensure_output_dir(output_base, rel_path)
        base_name = os.path.splitext(os.path.basename(full_path))[0]
        pdf_name = base_name + '.pdf'
        pdf_path = os.path.join(out_dir, pdf_name)

        print(f"转换中: {rel_path} -> {os.path.relpath(pdf_path, root_dir)}")

        ok, error = convert_md_to_pdf(
            full_path, pdf_path, args.font, args.margin,
            args.page_size, args.pdf_engine, args.pandoc_args, css_path
        )
        if ok:
            success_count += 1
        else:
            print(f"  失败:\n{error}", file=sys.stderr)
            fail_count += 1

    print(f"\n完成: 成功 {success_count} 个，失败 {fail_count} 个。")
    if not args.style:
        print(f"提示：临时 CSS 文件未删除，位于 {css_path}，可自行删除。")


if __name__ == '__main__':
    main()