#!/usr/bin/env python3
"""
图片处理工具使用示例
Image Processing Tool Usage Examples
"""

from image_processor import ImageProcessor
import cv2
import numpy as np
import os


def create_test_image_with_borders_and_skew():
    """创建一个带黑边和倾斜的测试图片"""
    # 创建一个简单的测试图片
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255  # 白色背景
    
    # 添加一些内容
    cv2.rectangle(img, (100, 100), (500, 300), (0, 0, 255), -1)  # 红色矩形
    cv2.putText(img, "Test Image", (200, 220), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    # 添加黑边
    bordered_img = np.zeros((500, 700, 3), dtype=np.uint8)  # 黑色背景
    bordered_img[50:450, 50:650] = img  # 将原图放在中间
    
    # 旋转图片制造倾斜
    center = (350, 250)
    rotation_matrix = cv2.getRotationMatrix2D(center, 5, 1.0)  # 5度倾斜
    skewed_img = cv2.warpAffine(bordered_img, rotation_matrix, (700, 500))
    
    # 再次添加黑边（模拟扫描后的效果）
    final_img = np.zeros((600, 800, 3), dtype=np.uint8)
    final_img[50:550, 50:750] = skewed_img
    
    return final_img


def demo_single_image():
    """演示单张图片处理"""
    print("=== 单张图片处理演示 ===")
    
    # 创建测试图片
    test_img = create_test_image_with_borders_and_skew()
    test_path = "/workspace/test_image.jpg"
    cv2.imwrite(test_path, test_img)
    print(f"创建测试图片: {test_path}")
    
    # 处理图片
    processor = ImageProcessor()
    processor.debug = True
    
    output_path = processor.process_image(
        test_path,
        "/workspace/test_image_processed.jpg",
        remove_borders=True,
        correct_skew=True,
        border_threshold=10
    )
    
    print(f"处理完成: {output_path}")


def demo_batch_processing():
    """演示批量处理"""
    print("\n=== 批量处理演示 ===")
    
    # 创建测试目录和多张测试图片
    test_dir = "/workspace/test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建几张不同的测试图片
    for i in range(3):
        # 创建不同大小和倾斜角度的图片
        size = (300 + i * 100, 400 + i * 50, 3)
        img = np.ones(size, dtype=np.uint8) * 255
        
        # 添加不同颜色的内容
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        cv2.rectangle(img, (50, 50), (size[1]-50, size[0]-50), colors[i], -1)
        cv2.putText(img, f"Image {i+1}", (100, size[0]//2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 添加黑边
        bordered_size = (size[0] + 100, size[1] + 100, 3)
        bordered_img = np.zeros(bordered_size, dtype=np.uint8)
        bordered_img[50:size[0]+50, 50:size[1]+50] = img
        
        # 添加不同程度的倾斜
        center = (bordered_size[1] // 2, bordered_size[0] // 2)
        angle = (i + 1) * 2  # 2, 4, 6度倾斜
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        skewed_img = cv2.warpAffine(bordered_img, rotation_matrix, 
                                   (bordered_size[1], bordered_size[0]))
        
        # 保存测试图片
        test_image_path = f"{test_dir}/test_image_{i+1}.jpg"
        cv2.imwrite(test_image_path, skewed_img)
        print(f"创建测试图片: {test_image_path}")
    
    # 批量处理
    processor = ImageProcessor()
    processor.debug = False  # 批量处理时关闭详细输出
    
    processor.process_batch(
        test_dir,
        f"{test_dir}/processed",
        remove_borders=True,
        correct_skew=True,
        border_threshold=10
    )


def show_usage_examples():
    """显示使用示例"""
    print("\n=== 使用方法 ===")
    print("1. 处理单张图片:")
    print("   python image_processor.py input.jpg -o output.jpg")
    print()
    print("2. 批量处理目录中的所有图片:")
    print("   python image_processor.py /path/to/images/ -o /path/to/output/")
    print()
    print("3. 只去黑边，不校正倾斜:")
    print("   python image_processor.py input.jpg --no-skew")
    print()
    print("4. 只校正倾斜，不去黑边:")
    print("   python image_processor.py input.jpg --no-borders")
    print()
    print("5. 调整黑边检测阈值:")
    print("   python image_processor.py input.jpg --threshold 20")
    print()
    print("6. 启用调试模式:")
    print("   python image_processor.py input.jpg --debug")


if __name__ == "__main__":
    print("图片处理工具演示")
    print("==================")
    
    try:
        # 演示单张图片处理
        demo_single_image()
        
        # 演示批量处理
        demo_batch_processing()
        
        # 显示使用方法
        show_usage_examples()
        
        print("\n演示完成！请查看生成的图片文件。")
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
        print("请确保已安装所需依赖: pip install -r requirements.txt")