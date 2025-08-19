#!/usr/bin/env python3
"""
图片处理工具 - 去黑边和校正倾斜
Image Processing Tool - Remove Black Borders and Correct Skew
"""

import cv2
import numpy as np
import argparse
import os
from pathlib import Path
from typing import Tuple, Optional
import math


class ImageProcessor:
    """图片处理类，用于去黑边和校正倾斜"""
    
    def __init__(self):
        self.debug = False
    
    def remove_black_borders(self, image: np.ndarray, threshold: int = 10) -> np.ndarray:
        """
        去除图片的黑边
        
        Args:
            image: 输入图片
            threshold: 黑色阈值，低于此值的像素被认为是黑色
            
        Returns:
            去除黑边后的图片
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 创建掩码，找出非黑色区域
        mask = gray > threshold
        
        # 找到非黑色像素的边界
        coords = np.argwhere(mask)
        if len(coords) == 0:
            return image  # 如果整个图片都是黑色，返回原图
        
        # 获取边界框
        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)
        
        # 裁剪图片
        cropped = image[y_min:y_max+1, x_min:x_max+1]
        
        if self.debug:
            print(f"原始尺寸: {image.shape}")
            print(f"裁剪后尺寸: {cropped.shape}")
            print(f"去除边界: 上{y_min}, 下{image.shape[0]-y_max-1}, 左{x_min}, 右{image.shape[1]-x_max-1}")
        
        return cropped
    
    def detect_skew_angle(self, image: np.ndarray) -> float:
        """
        检测图片的倾斜角度
        
        Args:
            image: 输入图片
            
        Returns:
            倾斜角度（度）
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 霍夫直线检测
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is None:
            return 0.0
        
        # 计算所有直线的角度
        angles = []
        for rho, theta in lines[:, 0]:
            angle = theta * 180 / np.pi
            # 将角度转换到 [-90, 90] 范围
            if angle > 90:
                angle = angle - 180
            elif angle < -90:
                angle = angle + 180
            angles.append(angle)
        
        # 使用中位数作为倾斜角度，更稳定
        if angles:
            skew_angle = np.median(angles)
            
            # 如果角度接近垂直，可能是检测到了垂直线条
            # 尝试检测水平线条
            if abs(skew_angle) > 45:
                horizontal_angles = [a for a in angles if abs(a) < 45]
                if horizontal_angles:
                    skew_angle = np.median(horizontal_angles)
            
            if self.debug:
                print(f"检测到的倾斜角度: {skew_angle:.2f}°")
            
            return skew_angle
        
        return 0.0
    
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        旋转图片校正倾斜
        
        Args:
            image: 输入图片
            angle: 旋转角度（度）
            
        Returns:
            旋转后的图片
        """
        if abs(angle) < 0.1:  # 角度太小，不需要旋转
            return image
        
        # 获取图片中心
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        
        # 计算旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 计算旋转后的图片尺寸
        cos_val = abs(rotation_matrix[0, 0])
        sin_val = abs(rotation_matrix[0, 1])
        new_w = int((h * sin_val) + (w * cos_val))
        new_h = int((h * cos_val) + (w * sin_val))
        
        # 调整旋转矩阵的平移部分
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        # 执行旋转
        rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), 
                                flags=cv2.INTER_CUBIC, 
                                borderMode=cv2.BORDER_CONSTANT,
                                borderValue=(0, 0, 0))
        
        if self.debug:
            print(f"旋转角度: {angle:.2f}°")
            print(f"旋转前尺寸: {image.shape}")
            print(f"旋转后尺寸: {rotated.shape}")
        
        return rotated
    
    def process_image(self, image_path: str, output_path: Optional[str] = None, 
                     remove_borders: bool = True, correct_skew: bool = True,
                     border_threshold: int = 10) -> str:
        """
        处理单张图片
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径，如果为None则自动生成
            remove_borders: 是否去除黑边
            correct_skew: 是否校正倾斜
            border_threshold: 黑边检测阈值
            
        Returns:
            输出文件路径
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
        
        original_image = image.copy()
        
        print(f"处理图片: {image_path}")
        print(f"原始尺寸: {image.shape[1]}x{image.shape[0]}")
        
        # 步骤1: 去除黑边
        if remove_borders:
            print("正在去除黑边...")
            image = self.remove_black_borders(image, border_threshold)
        
        # 步骤2: 校正倾斜
        if correct_skew:
            print("正在检测和校正倾斜...")
            skew_angle = self.detect_skew_angle(image)
            if abs(skew_angle) > 0.1:
                image = self.rotate_image(image, -skew_angle)  # 负号用于校正
                
                # 旋转后可能产生新的黑边，再次去除
                if remove_borders:
                    image = self.remove_black_borders(image, border_threshold)
        
        # 生成输出路径
        if output_path is None:
            input_path = Path(image_path)
            output_path = str(input_path.parent / f"{input_path.stem}_processed{input_path.suffix}")
        
        # 保存处理后的图片
        cv2.imwrite(output_path, image)
        print(f"处理完成，保存到: {output_path}")
        print(f"最终尺寸: {image.shape[1]}x{image.shape[0]}")
        
        return output_path
    
    def process_batch(self, input_dir: str, output_dir: Optional[str] = None,
                     remove_borders: bool = True, correct_skew: bool = True,
                     border_threshold: int = 10):
        """
        批量处理图片
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录，如果为None则在输入目录创建processed子目录
            remove_borders: 是否去除黑边
            correct_skew: 是否校正倾斜
            border_threshold: 黑边检测阈值
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"输入目录不存在: {input_dir}")
        
        # 设置输出目录
        if output_dir is None:
            output_path = input_path / "processed"
        else:
            output_path = Path(output_dir)
        
        output_path.mkdir(exist_ok=True)
        
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        # 查找所有图片文件
        image_files = []
        for ext in image_extensions:
            image_files.extend(input_path.glob(f"*{ext}"))
            image_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not image_files:
            print(f"在目录 {input_dir} 中没有找到图片文件")
            return
        
        print(f"找到 {len(image_files)} 张图片，开始批量处理...")
        
        success_count = 0
        for i, image_file in enumerate(image_files, 1):
            try:
                output_file = output_path / image_file.name
                print(f"\n[{i}/{len(image_files)}] 处理: {image_file.name}")
                
                self.process_image(
                    str(image_file), 
                    str(output_file),
                    remove_borders=remove_borders,
                    correct_skew=correct_skew,
                    border_threshold=border_threshold
                )
                success_count += 1
                
            except Exception as e:
                print(f"处理 {image_file.name} 时出错: {e}")
        
        print(f"\n批量处理完成！成功处理 {success_count}/{len(image_files)} 张图片")
        print(f"输出目录: {output_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="图片去黑边和校正倾斜工具")
    parser.add_argument("input", help="输入图片文件或目录路径")
    parser.add_argument("-o", "--output", help="输出文件或目录路径")
    parser.add_argument("--no-borders", action="store_true", help="不去除黑边")
    parser.add_argument("--no-skew", action="store_true", help="不校正倾斜")
    parser.add_argument("--threshold", type=int, default=10, help="黑边检测阈值 (默认: 10)")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    processor = ImageProcessor()
    processor.debug = args.debug
    
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"错误: 输入路径不存在: {args.input}")
        return
    
    try:
        if input_path.is_file():
            # 处理单个文件
            processor.process_image(
                args.input,
                args.output,
                remove_borders=not args.no_borders,
                correct_skew=not args.no_skew,
                border_threshold=args.threshold
            )
        elif input_path.is_dir():
            # 批量处理目录
            processor.process_batch(
                args.input,
                args.output,
                remove_borders=not args.no_borders,
                correct_skew=not args.no_skew,
                border_threshold=args.threshold
            )
        else:
            print(f"错误: 不支持的输入类型: {args.input}")
            
    except Exception as e:
        print(f"处理过程中发生错误: {e}")


if __name__ == "__main__":
    main()