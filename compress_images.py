"""
图片压缩脚本
- JPEG: 最长边缩到 2000px, 质量 80%
- PNG: 最长边缩到 1500px, 保持 PNG 格式(保留透明), 优化压缩
- 同名覆盖, 不修改 HTML 代码
"""
import os
import sys
from PIL import Image

# 素材根目录
BASE = r"素材照片、视频和文稿"

# 配置
JPEG_MAX_SIZE = 2000   # JPEG 最长边像素
PNG_MAX_SIZE = 1500    # PNG 最长边像素
JPEG_QUALITY = 80      # JPEG 质量 (0-100)

def compress_image(filepath):
    """返回 (original_size, new_size) 单位: MB"""
    original_size = os.path.getsize(filepath)
    ext = os.path.splitext(filepath)[1].lower()

    try:
        img = Image.open(filepath)

        # 转换为 RGB（如果不是的话）
        if ext in ('.jpg', '.jpeg') and img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')

        # 确定最大尺寸
        if ext in ('.jpg', '.jpeg'):
            max_size = JPEG_MAX_SIZE
        else:
            max_size = PNG_MAX_SIZE

        # 如果图片本身就很小，不放大
        w, h = img.size
        longest = max(w, h)
        if longest > max_size:
            ratio = max_size / longest
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
            print(f"  缩放: {w}x{h} -> {new_w}x{new_h}")

        # 保存
        if ext in ('.jpg', '.jpeg'):
            img.save(filepath, 'JPEG', quality=JPEG_QUALITY, optimize=True)
        elif ext == '.png':
            # PNG 先转成调色板模式如果有透明, 否则优化保存
            if img.mode == 'RGBA':
                img.save(filepath, 'PNG', optimize=True)
            else:
                img.save(filepath, 'PNG', optimize=True)

        new_size = os.path.getsize(filepath)
        return (original_size, new_size)

    except Exception as e:
        print(f"  [X] 处理失败: {e}")
        return (original_size, original_size)


def main():
    if not os.path.exists(BASE):
        print(f"找不到目录: {BASE}")
        return

    # 收集所有图片
    images = []
    for root, dirs, files in os.walk(BASE):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(os.path.join(root, f))

    print(f"找到 {len(images)} 张图片\n")

    total_orig = 0
    total_new = 0

    for i, img_path in enumerate(images, 1):
        orig_mb = os.path.getsize(img_path) / (1024 * 1024)
        rel_path = os.path.relpath(img_path, BASE)
        print(f"[{i}/{len(images)}] {rel_path} ({orig_mb:.1f}MB)")

        orig_bytes, new_bytes = compress_image(img_path)
        total_orig += orig_bytes
        total_new += new_bytes

        saved = (orig_bytes - new_bytes) / (1024 * 1024)
        pct = (1 - new_bytes / orig_bytes) * 100 if orig_bytes > 0 else 0
        print(f"  [OK] {orig_bytes/(1024**2):.1f}MB -> {new_bytes/(1024**2):.1f}MB, 节省 {saved:.1f}MB ({pct:.0f}%)\n")

    print("=" * 50)
    print(f"总计: {total_orig/(1024**2):.1f}MB → {total_new/(1024**2):.1f}MB")
    print(f"节省: {(total_orig - total_new)/(1024**2):.1f}MB ({(1 - total_new/total_orig)*100:.0f}%)")
    print("全部完成喵~")

if __name__ == '__main__':
    main()
