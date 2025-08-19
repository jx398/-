#!/usr/bin/env python3
"""
快速图片处理工具 - 简化版
Quick Image Processing Tool - Simplified Version
"""

import cv2
import numpy as np
import sys
import os
from pathlib import Path


def process_image_quick(input_path, output_path=None):
    """快速处理图片：去黑边 + 校正倾斜"""
    
    # 读取图片
    image = cv2.imread(input_path)
    if image is None:
        print(f"❌ 无法读取图片: {input_path}")
        return None
    
    print(f"📸 处理图片: {os.path.basename(input_path)}")
    print(f"   原始尺寸: {image.shape[1]}x{image.shape[0]}")
    
    # 1. 去除黑边
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = gray > 10  # 黑色阈值
    coords = np.argwhere(mask)
    
    if len(coords) > 0:
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        image = image[y_min:y_max+1, x_min:x_max+1]
        print(f"   去除黑边: 上{y_min} 下{gray.shape[0]-y_max-1} 左{x_min} 右{gray.shape[1]-x_max-1}")
    
    # 2. 检测倾斜角度
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
    
    if lines is not None:
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            if angle > 90:
                angle = angle - 180
            elif angle < -90:
                angle = angle + 180
            angles.append(angle)
        
        if angles:
            skew_angle = np.median(angles)
            if abs(skew_angle) > 45:
                horizontal_angles = [a for a in angles if abs(a) < 45]
                if horizontal_angles:
                    skew_angle = np.median(horizontal_angles)
            
            # 3. 校正倾斜
            if abs(skew_angle) > 0.5:
                print(f"   检测倾斜: {skew_angle:.1f}°")
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, -skew_angle, 1.0)
                
                # 计算新尺寸
                cos_val = abs(rotation_matrix[0, 0])
                sin_val = abs(rotation_matrix[0, 1])
                new_w = int((h * sin_val) + (w * cos_val))
                new_h = int((h * cos_val) + (w * sin_val))
                
                rotation_matrix[0, 2] += (new_w / 2) - center[0]
                rotation_matrix[1, 2] += (new_h / 2) - center[1]
                
                image = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), 
                                     flags=cv2.INTER_CUBIC, 
                                     borderMode=cv2.BORDER_CONSTANT,
                                     borderValue=(0, 0, 0))
                
                # 再次去除黑边（旋转后可能产生）
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                mask = gray > 10
                coords = np.argwhere(mask)
                if len(coords) > 0:
                    y_min, x_min = coords.min(axis=0)
                    y_max, x_max = coords.max(axis=0)
                    image = image[y_min:y_max+1, x_min:x_max+1]
            else:
                print(f"   倾斜角度很小({skew_angle:.1f}°)，无需校正")
    
    # 4. 保存结果
    if output_path is None:
        input_path_obj = Path(input_path)
        output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_fixed{input_path_obj.suffix}")
    
    cv2.imwrite(output_path, image)
    print(f"✅ 处理完成: {os.path.basename(output_path)}")
    print(f"   最终尺寸: {image.shape[1]}x{image.shape[0]}")
    
    return output_path


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python quick_process.py <图片路径> [输出路径]")
        print("示例: python quick_process.py photo.jpg")
        print("示例: python quick_process.py photo.jpg fixed_photo.jpg")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_path):
        print(f"❌ 文件不存在: {input_path}")
        return
    
    try:
        result = process_image_quick(input_path, output_path)
        if result:
            print(f"\n🎉 成功！输出文件: {result}")
    except Exception as e:
        print(f"❌ 处理失败: {e}")


if __name__ == "__main__":
    main()