#!/usr/bin/env python3
"""
图片处理工具：去黑边和校正倾斜
支持批量处理图片，自动检测并去除黑边，校正图片倾斜
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path
from typing import Tuple, Optional
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理类，包含去黑边和校正倾斜功能"""
    
    def __init__(self, black_threshold: int = 30, angle_threshold: float = 0.5):
        """
        初始化图片处理器
        
        Args:
            black_threshold: 黑边检测阈值，像素值低于此值被认为是黑色
            angle_threshold: 角度阈值，小于此角度的倾斜将被忽略
        """
        self.black_threshold = black_threshold
        self.angle_threshold = angle_threshold
    
    def detect_black_borders(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        检测图片的黑边
        
        Args:
            image: 输入图片
            
        Returns:
            (top, bottom, left, right) 黑边的边界坐标
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 创建二值化图像
        _, binary = cv2.threshold(gray, self.black_threshold, 255, cv2.THRESH_BINARY)
        
        # 查找非零像素的边界
        coords = cv2.findNonZero(binary)
        if coords is None:
            return 0, image.shape[0], 0, image.shape[1]
        
        x, y, w, h = cv2.boundingRect(coords)
        
        return y, y + h, x, x + w
    
    def remove_black_borders(self, image: np.ndarray) -> np.ndarray:
        """
        去除图片黑边
        
        Args:
            image: 输入图片
            
        Returns:
            去除黑边后的图片
        """
        top, bottom, left, right = self.detect_black_borders(image)
        
        # 确保边界有效
        top = max(0, top)
        bottom = min(image.shape[0], bottom)
        left = max(0, left)
        right = min(image.shape[1], right)
        
        if bottom <= top or right <= left:
            logger.warning("检测到的边界无效，返回原图")
            return image
        
        cropped = image[top:bottom, left:right]
        logger.info(f"去除黑边：原尺寸 {image.shape[:2]} -> 新尺寸 {cropped.shape[:2]}")
        
        return cropped
    
    def detect_skew_angle(self, image: np.ndarray) -> float:
        """
        检测图片的倾斜角度
        
        Args:
            image: 输入图片
            
        Returns:
            倾斜角度（度数）
        """
        # 转换为灰度图
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # 边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 霍夫变换检测直线
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is None:
            return 0.0
        
        # 计算角度
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            # 只考虑接近水平或垂直的线
            if abs(angle) < 45:
                angles.append(angle)
            elif abs(angle - 90) < 45:
                angles.append(angle - 90)
            elif abs(angle + 90) < 45:
                angles.append(angle + 90)
        
        if not angles:
            return 0.0
        
        # 使用中位数作为最终角度
        median_angle = np.median(angles)
        
        return median_angle
    
    def correct_skew(self, image: np.ndarray, angle: Optional[float] = None) -> np.ndarray:
        """
        校正图片倾斜
        
        Args:
            image: 输入图片
            angle: 指定的倾斜角度，如果为None则自动检测
            
        Returns:
            校正后的图片
        """
        if angle is None:
            angle = self.detect_skew_angle(image)
        
        if abs(angle) < self.angle_threshold:
            logger.info(f"倾斜角度 {angle:.2f}° 小于阈值，无需校正")
            return image
        
        logger.info(f"检测到倾斜角度：{angle:.2f}°，开始校正")
        
        # 获取图片中心点
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        
        # 创建旋转矩阵
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # 计算旋转后的边界
        cos_angle = abs(rotation_matrix[0, 0])
        sin_angle = abs(rotation_matrix[0, 1])
        
        new_w = int((h * sin_angle) + (w * cos_angle))
        new_h = int((h * cos_angle) + (w * sin_angle))
        
        # 调整旋转矩阵的平移部分
        rotation_matrix[0, 2] += (new_w / 2) - center[0]
        rotation_matrix[1, 2] += (new_h / 2) - center[1]
        
        # 执行旋转
        rotated = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), 
                                flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, 
                                borderValue=(0, 0, 0))
        
        return rotated
    
    def process_image(self, image_path: str, output_path: str = None, 
                     remove_borders: bool = True, correct_skew_flag: bool = True) -> str:
        """
        处理单张图片
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径，如果为None则自动生成
            remove_borders: 是否去除黑边
            correct_skew_flag: 是否校正倾斜
            
        Returns:
            输出图片路径
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"无法读取图片：{image_path}")
        
        logger.info(f"开始处理图片：{image_path}")
        original_shape = image.shape[:2]
        
        # 去除黑边
        if remove_borders:
            image = self.remove_black_borders(image)
        
        # 校正倾斜
        if correct_skew_flag:
            image = self.correct_skew(image)
        
        # 生成输出路径
        if output_path is None:
            input_path = Path(image_path)
            output_path = str(input_path.parent / f"{input_path.stem}_processed{input_path.suffix}")
        
        # 保存图片
        cv2.imwrite(output_path, image)
        logger.info(f"处理完成：{original_shape} -> {image.shape[:2]}，保存到：{output_path}")
        
        return output_path
    
    def process_batch(self, input_dir: str, output_dir: str = None, 
                     remove_borders: bool = True, correct_skew_flag: bool = True) -> list:
        """
        批量处理图片
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录，如果为None则在输入目录下创建processed文件夹
            remove_borders: 是否去除黑边
            correct_skew_flag: 是否校正倾斜
            
        Returns:
            处理后的图片路径列表
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"输入目录不存在：{input_dir}")
        
        # 设置输出目录
        if output_dir is None:
            output_path = input_path / "processed"
        else:
            output_path = Path(output_dir)
        
        output_path.mkdir(exist_ok=True)
        
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        # 查找所有图片文件
        image_files = [f for f in input_path.iterdir() 
                      if f.is_file() and f.suffix.lower() in image_extensions]
        
        if not image_files:
            logger.warning(f"在目录 {input_dir} 中未找到支持的图片文件")
            return []
        
        logger.info(f"找到 {len(image_files)} 张图片，开始批量处理")
        
        processed_files = []
        for image_file in image_files:
            try:
                output_file = output_path / image_file.name
                result = self.process_image(str(image_file), str(output_file), 
                                          remove_borders, correct_skew_flag)
                processed_files.append(result)
            except Exception as e:
                logger.error(f"处理图片 {image_file} 时出错：{e}")
        
        logger.info(f"批量处理完成，成功处理 {len(processed_files)} 张图片")
        return processed_files


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片处理工具：去黑边和校正倾斜')
    parser.add_argument('input', help='输入图片文件或目录路径')
    parser.add_argument('-o', '--output', help='输出路径')
    parser.add_argument('--no-borders', action='store_true', help='不去除黑边')
    parser.add_argument('--no-skew', action='store_true', help='不校正倾斜')
    parser.add_argument('--black-threshold', type=int, default=30, 
                       help='黑边检测阈值 (默认: 30)')
    parser.add_argument('--angle-threshold', type=float, default=0.5, 
                       help='角度阈值，小于此值的倾斜将被忽略 (默认: 0.5)')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    
    args = parser.parse_args()
    
    # 创建图片处理器
    processor = ImageProcessor(
        black_threshold=args.black_threshold,
        angle_threshold=args.angle_threshold
    )
    
    try:
        input_path = Path(args.input)
        
        if args.batch or input_path.is_dir():
            # 批量处理
            processor.process_batch(
                input_dir=args.input,
                output_dir=args.output,
                remove_borders=not args.no_borders,
                correct_skew_flag=not args.no_skew
            )
        else:
            # 单文件处理
            processor.process_image(
                image_path=args.input,
                output_path=args.output,
                remove_borders=not args.no_borders,
                correct_skew_flag=not args.no_skew
            )
        
        print("处理完成！")
        
    except Exception as e:
        logger.error(f"处理失败：{e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())