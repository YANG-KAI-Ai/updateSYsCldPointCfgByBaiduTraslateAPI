## README

### 项目名称: 数据字段翻译和标准化

### 项目描述
本项目旨在通过调用百度翻译API，将数据库表`sys_cld_point_cfg`中的`comment`字段内容翻译为英文，并生成相应的标准化字段名。生成的字段名将用于更新数据库中的`field_name`字段。

### 主要依赖
- pandas
- mysql.connector
- requests
- sqlalchemy

### 安装依赖
在运行该项目之前，请确保已经安装所需的Python库。可以通过以下命令安装：
```bash
pip install pandas mysql-connector-python requests sqlalchemy
```

### 百度翻译 API 配置
请确保你已经注册了百度翻译API，并获取了appid和密钥。将以下信息替换为你的百度翻译API的appid和密钥：
```python
appid = '你的appid'
secretKey = '你的密钥'
```

### 脚本功能

1. **批量翻译函数**：
    - `baidu_translate_batch(queries, from_lang='zh', to_lang='en')`：用于批量翻译评论内容，避免一次性请求过多而导致失败。

2. **字段名格式化函数**：
    - `format_field_name(translation)`：用于将翻译后的字段名进行格式化，删除特殊字符并限制长度。

3. **归一化函数**：
    - `normalize_comment(comment)`：去除`comment`字段中的数字部分。

4. **数据库连接和数据读取**：
    - 使用SQLAlchemy和MySQL连接器连接数据库，读取数据表`sys_cld_point_cfg`中的数据。

5. **数据处理和更新**：
    - 读取数据后，对`comment`字段进行归一化处理，并分批调用百度翻译API进行翻译。
    - 将翻译结果格式化为标准字段名，并根据映射关系更新`field_name`字段。
    - 将处理后的数据写回数据库。

### 使用方法
运行脚本之前，请确保已正确配置数据库连接信息和百度翻译API信息。将脚本保存为`translate_and_update.py`，然后通过以下命令运行：
```bash
python translate_and_update.py
```

### 注意事项
- 为了避免频繁请求百度翻译API导致的限制，每批翻译后脚本会等待1秒再进行下一次请求。
- 请确保数据库连接信息和百度翻译API信息的正确性，以避免请求失败和数据更新失败。

### 作者
杨凯 - Java工程师，有四年工作经验，熟悉Python和数据库操作。
