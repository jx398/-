# 图片处理工具 - 去黑边和校正倾斜

这是一个功能强大的Python图片处理工具，可以自动去除图片的黑边并校正倾斜的图片。特别适用于处理扫描文档、照片等需要后期处理的图片。

## 功能特性

- ✅ **自动去除黑边**: 智能检测并移除图片周围的黑色边框
- ✅ **倾斜校正**: 使用霍夫直线检测算法自动检测和校正图片倾斜
- ✅ **批量处理**: 支持对整个目录中的图片进行批量处理
- ✅ **多格式支持**: 支持 JPG, PNG, BMP, TIFF 等常见图片格式
- ✅ **参数可调**: 可自定义黑边检测阈值等参数
- ✅ **调试模式**: 提供详细的处理过程信息

## 安装依赖

```bash
pip install -r requirements.txt
```

需要的依赖包：
- opencv-python >= 4.8.0
- numpy >= 1.21.0

## 使用方法

### 1. 处理单张图片

```bash
# 基本用法
python image_processor.py input.jpg

# 指定输出文件
python image_processor.py input.jpg -o output.jpg

# 启用调试模式
python image_processor.py input.jpg --debug
```

### 2. 批量处理

```bash
# 处理整个目录
python image_processor.py /path/to/images/

# 指定输出目录
python image_processor.py /path/to/images/ -o /path/to/output/
```

### 3. 高级选项

```bash
# 只去黑边，不校正倾斜
python image_processor.py input.jpg --no-skew

# 只校正倾斜，不去黑边
python image_processor.py input.jpg --no-borders

# 调整黑边检测阈值（默认为10）
python image_processor.py input.jpg --threshold 20
```

## 参数说明

- `input`: 输入图片文件或目录路径
- `-o, --output`: 输出文件或目录路径（可选）
- `--no-borders`: 禁用黑边去除功能
- `--no-skew`: 禁用倾斜校正功能
- `--threshold`: 黑边检测阈值，数值越低检测越敏感（默认：10）
- `--debug`: 启用调试模式，显示详细处理信息

## 处理流程

1. **读取图片**: 支持多种常见格式
2. **去除黑边**: 
   - 转换为灰度图
   - 检测非黑色像素区域
   - 计算最小边界框
   - 裁剪图片
3. **倾斜检测**:
   - 边缘检测（Canny算法）
   - 霍夫直线检测
   - 计算倾斜角度
4. **倾斜校正**:
   - 计算旋转矩阵
   - 应用仿射变换
   - 调整图片尺寸
5. **二次去黑边**: 旋转后可能产生新的黑边，再次处理
6. **保存结果**: 输出处理后的图片

## 示例代码

### Python API 使用

```python
from image_processor import ImageProcessor

# 创建处理器实例
processor = ImageProcessor()
processor.debug = True  # 启用调试

# 处理单张图片
output_path = processor.process_image(
    "input.jpg",
    "output.jpg",
    remove_borders=True,
    correct_skew=True,
    border_threshold=10
)

# 批量处理
processor.process_batch(
    "input_directory/",
    "output_directory/",
    remove_borders=True,
    correct_skew=True
)
```

### 运行演示

```bash
python demo_usage.py
```

这将创建测试图片并演示各种处理功能。

## 技术细节

### 黑边检测算法
- 使用灰度阈值检测黑色区域
- 通过 `np.argwhere()` 找到非黑色像素坐标
- 计算最小边界框进行裁剪

### 倾斜检测算法
- Canny边缘检测提取图片边缘
- 霍夫直线检测找到主要直线
- 统计直线角度，使用中位数作为倾斜角度
- 自动过滤垂直线干扰

### 图片旋转
- 使用 `cv2.getRotationMatrix2D()` 计算旋转矩阵
- 自动计算旋转后的图片尺寸
- 使用双三次插值保证图片质量

## 注意事项

1. **图片质量**: 建议输入图片有足够的分辨率，太小的图片可能影响检测精度
2. **倾斜角度**: 工具可以处理 ±45° 范围内的倾斜，超出此范围可能检测不准确
3. **黑边阈值**: 根据图片特点调整阈值，扫描文档建议使用较低阈值（5-15）
4. **批量处理**: 大量图片处理时建议关闭调试模式以提高速度

## 支持的图片格式

- JPG/JPEG
- PNG
- BMP
- TIFF/TIF

## 故障排除

### 常见问题

1. **ImportError**: 确保已安装所有依赖 `pip install -r requirements.txt`
2. **图片无法读取**: 检查文件路径和格式是否正确
3. **倾斜检测不准确**: 尝试调整图片质量或使用不同的输入图片
4. **黑边去除过度**: 增加阈值参数 `--threshold 20`

### 性能优化

- 批量处理时关闭调试模式
- 对于大图片，可以考虑先缩放再处理
- 使用SSD存储可以提高I/O速度

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！