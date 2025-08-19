# 图片处理工具

一个用于去除图片黑边并校正倾斜的Python工具。

## 功能特点

- **去除黑边**：自动检测并裁剪图片周围的黑色边框
- **校正倾斜**：使用霍夫变换检测并校正图片倾斜
- **批量处理**：支持批量处理整个目录的图片
- **灵活配置**：可自定义黑边检测阈值和角度阈值
- **多种格式**：支持常见图片格式（JPG、PNG、BMP、TIFF等）

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- opencv-python >= 4.5.0
- numpy >= 1.21.0

## 使用方法

### 1. 命令行使用

#### 处理单张图片
```bash
python image_processor.py input.jpg -o output.jpg
```

#### 批量处理目录
```bash
python image_processor.py input_dir --batch -o output_dir
```

#### 高级选项
```bash
# 只去黑边，不校正倾斜
python image_processor.py input.jpg --no-skew

# 只校正倾斜，不去黑边
python image_processor.py input.jpg --no-borders

# 自定义阈值
python image_processor.py input.jpg --black-threshold 50 --angle-threshold 1.0
```

### 2. 作为模块使用

```python
from image_processor import ImageProcessor

# 创建处理器
processor = ImageProcessor(black_threshold=30, angle_threshold=0.5)

# 处理单张图片
output_path = processor.process_image(
    image_path="input.jpg",
    output_path="output.jpg",
    remove_borders=True,
    correct_skew_flag=True
)

# 批量处理
processed_files = processor.process_batch(
    input_dir="input_folder",
    output_dir="output_folder"
)
```

## 参数说明

- `black_threshold`: 黑边检测阈值（0-255），默认30。像素值低于此值被认为是黑色
- `angle_threshold`: 角度阈值（度），默认0.5。小于此角度的倾斜将被忽略
- `remove_borders`: 是否去除黑边，默认True
- `correct_skew_flag`: 是否校正倾斜，默认True

## 算法原理

### 黑边检测
1. 将图片转换为灰度图
2. 使用阈值二值化
3. 查找非零像素的边界矩形
4. 根据边界裁剪图片

### 倾斜校正
1. 使用Canny边缘检测
2. 霍夫变换检测直线
3. 分析直线角度，计算倾斜角度
4. 使用仿射变换校正图片

## 示例代码

运行示例代码查看详细用法：

```bash
python example_usage.py
```

示例包括：
- 单张图片处理
- 批量处理
- 自定义参数使用
- 角度检测测试

## 输出示例

```
2024-01-01 12:00:00 - INFO - 开始处理图片：input.jpg
2024-01-01 12:00:00 - INFO - 去除黑边：原尺寸 (500, 700) -> 新尺寸 (400, 600)
2024-01-01 12:00:00 - INFO - 检测到倾斜角度：3.45°，开始校正
2024-01-01 12:00:00 - INFO - 处理完成：(500, 700) -> (420, 580)，保存到：output.jpg
```

## 注意事项

1. 确保输入图片路径正确且文件存在
2. 输出目录需要有写入权限
3. 处理大图片时可能需要较多内存
4. 角度检测基于直线特征，对于没有明显直线的图片效果可能不佳
5. 黑边检测阈值需要根据实际图片调整

## 故障排除

- **无法读取图片**：检查文件路径和格式是否支持
- **角度检测不准确**：调整angle_threshold或确保图片有明显的水平/垂直线条
- **黑边检测失效**：调整black_threshold值
- **内存不足**：处理大图片时考虑降低图片分辨率

## 许可证

MIT License