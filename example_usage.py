#!/usr/bin/env python3
"""
图片处理工具使用示例
演示如何使用ImageProcessor类处理图片
"""

import cv2
import numpy as np
from image_processor import ImageProcessor
import os

def create_test_image():
    """创建一个带黑边和倾斜的测试图片"""
    # 创建一个白色矩形图片
    img = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    # 在中间画一些内容
    cv2.rectangle(img, (100, 100), (500, 300), (0, 255, 0), -1)
    cv2.putText(img, "Test Image", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
    
    # 添加黑边
    bordered_img = np.zeros((500, 700, 3), dtype=np.uint8)
    bordered_img[50:450, 50:650] = img
    
    # 旋转图片（添加倾斜）
    center = (350, 250)
    rotation_matrix = cv2.getRotationMatrix2D(center, 5, 1.0)  # 倾斜5度
    skewed_img = cv2.warpAffine(bordered_img, rotation_matrix, (700, 500))
    
    return skewed_img

def example_single_image():
    """单张图片处理示例"""
    print("=== 单张图片处理示例 ===")
    
    # 创建测试图片
    test_img = create_test_image()
    test_path = "/workspace/test_image.jpg"
    cv2.imwrite(test_path, test_img)
    print(f"创建测试图片：{test_path}")
    
    # 创建处理器
    processor = ImageProcessor(black_threshold=30, angle_threshold=0.5)
    
    # 处理图片
    output_path = processor.process_image(
        image_path=test_path,
        output_path="/workspace/processed_image.jpg",
        remove_borders=True,
        correct_skew_flag=True
    )
    
    print(f"处理完成，输出文件：{output_path}")
    
    # 显示处理前后对比（如果有显示环境）
    try:
        original = cv2.imread(test_path)
        processed = cv2.imread(output_path)
        
        print(f"原图尺寸：{original.shape[:2]}")
        print(f"处理后尺寸：{processed.shape[:2]}")
        
        # 如果环境支持显示，可以取消注释以下代码
        # cv2.imshow('Original', original)
        # cv2.imshow('Processed', processed)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"显示图片时出错：{e}")

def example_batch_processing():
    """批量处理示例"""
    print("\n=== 批量处理示例 ===")
    
    # 创建测试目录和多张图片
    test_dir = "/workspace/test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建几张不同的测试图片
    for i in range(3):
        # 创建不同角度的倾斜图片
        img = np.ones((300, 400, 3), dtype=np.uint8) * 255
        cv2.rectangle(img, (50, 50), (350, 250), (0, 255, 0), -1)
        cv2.putText(img, f"Image {i+1}", (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # 添加黑边
        bordered_img = np.zeros((400, 500, 3), dtype=np.uint8)
        bordered_img[50:350, 50:450] = img
        
        # 添加不同角度的倾斜
        center = (250, 200)
        angle = (i - 1) * 3  # -3, 0, 3 度
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        skewed_img = cv2.warpAffine(bordered_img, rotation_matrix, (500, 400))
        
        test_path = os.path.join(test_dir, f"test_{i+1}.jpg")
        cv2.imwrite(test_path, skewed_img)
        print(f"创建测试图片：{test_path}")
    
    # 批量处理
    processor = ImageProcessor()
    processed_files = processor.process_batch(
        input_dir=test_dir,
        output_dir=os.path.join(test_dir, "processed"),
        remove_borders=True,
        correct_skew_flag=True
    )
    
    print(f"批量处理完成，处理了 {len(processed_files)} 张图片")
    for file in processed_files:
        print(f"  - {file}")

def example_custom_parameters():
    """自定义参数示例"""
    print("\n=== 自定义参数示例 ===")
    
    # 创建一个轻微倾斜的图片
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.rectangle(img, (100, 100), (300, 200), (255, 0, 0), -1)
    
    # 添加很小的黑边
    bordered_img = np.zeros((320, 420, 3), dtype=np.uint8)
    bordered_img[10:310, 10:410] = img
    
    # 轻微倾斜
    center = (210, 160)
    rotation_matrix = cv2.getRotationMatrix2D(center, 0.3, 1.0)  # 很小的角度
    skewed_img = cv2.warpAffine(bordered_img, rotation_matrix, (420, 320))
    
    test_path = "/workspace/slight_skew.jpg"
    cv2.imwrite(test_path, skewed_img)
    
    # 使用不同的参数设置
    print("使用严格参数（小阈值）：")
    strict_processor = ImageProcessor(black_threshold=10, angle_threshold=0.1)
    strict_output = strict_processor.process_image(test_path, "/workspace/strict_processed.jpg")
    
    print("使用宽松参数（大阈值）：")
    loose_processor = ImageProcessor(black_threshold=50, angle_threshold=1.0)
    loose_output = loose_processor.process_image(test_path, "/workspace/loose_processed.jpg")
    
    print(f"严格处理结果：{strict_output}")
    print(f"宽松处理结果：{loose_output}")

def example_angle_detection():
    """角度检测示例"""
    print("\n=== 角度检测示例 ===")
    
    processor = ImageProcessor()
    
    # 测试不同角度的图片
    angles = [0, 2, 5, 10, -3, -7]
    
    for angle in angles:
        # 创建倾斜图片
        img = np.ones((200, 300, 3), dtype=np.uint8) * 255
        cv2.rectangle(img, (50, 50), (250, 150), (0, 255, 0), -1)
        cv2.line(img, (0, 100), (300, 100), (0, 0, 255), 2)  # 水平线用于检测
        
        center = (150, 100)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_img = cv2.warpAffine(img, rotation_matrix, (300, 200))
        
        # 检测角度
        detected_angle = processor.detect_skew_angle(rotated_img)
        print(f"实际角度：{angle:6.1f}°, 检测角度：{detected_angle:6.1f}°, "
              f"误差：{abs(angle - detected_angle):6.1f}°")

if __name__ == "__main__":
    print("图片处理工具使用示例")
    print("=" * 50)
    
    try:
        # 运行所有示例
        example_single_image()
        example_batch_processing()
        example_custom_parameters()
        example_angle_detection()
        
        print("\n所有示例运行完成！")
        print("你可以查看生成的图片文件来验证处理效果。")
        
    except Exception as e:
        print(f"运行示例时出错：{e}")
        import traceback
        traceback.print_exc()