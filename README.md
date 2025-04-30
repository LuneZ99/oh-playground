# 上交所 ETF 成份股信息爬虫

这个项目提供了一个Python脚本，用于从上海证券交易所（SSE）网站爬取ETF基金的成份股信息，并将数据保存为CSV文件。

## 功能

- 从上交所ETF详情页面爬取成份股信息
- 支持任意ETF基金ID
- 将爬取的数据保存为CSV文件
- 提供命令行界面，方便使用

## 依赖项

- Python 3.6+
- pandas
- selenium
- Chrome浏览器
- ChromeDriver

## 安装

1. 克隆或下载此仓库
2. 安装依赖项：

```bash
pip install pandas selenium
```

3. 安装Chrome浏览器和ChromeDriver（如果尚未安装）

## 使用方法

### 基本用法

```bash
python etf_scraper_final.py [fund_id]
```

其中 `[fund_id]` 是ETF基金的ID，例如 `511090`。如果不提供基金ID，默认使用 `511090`。

### 示例

爬取基金ID为 `510050` 的ETF成份股信息：

```bash
python etf_scraper_final.py 510050
```

指定输出目录：

```bash
python etf_scraper_final.py 510050 -o /path/to/output/directory
```

### 输出

脚本将生成一个名为 `etf_[fund_id]_components.csv` 的CSV文件，其中包含以下信息：

- 证券代码
- 证券简称
- 证券数量(手)
- 现金替代标志
- 申购现金替代溢价比率
- 赎回现金替代折价比率
- 替代金额(单位：人民币元)

## 脚本说明

本项目包含以下几个脚本：

1. `etf_scraper_final.py` - 最终版本，推荐使用
2. `etf_api_scraper.py` - 尝试使用API方式获取数据（不稳定）
3. `etf_selenium_scraper.py` - 使用Selenium爬取页面的初始版本
4. `etf_table_scraper.py` - 专注于提取表格数据的版本

## 注意事项

- 网站结构可能会变化，导致脚本失效
- 请合理控制爬取频率，避免对网站造成过大负担
- 爬取的数据仅供参考，交易决策请以官方数据为准

## 许可证

MIT