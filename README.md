# ly-genealogy（屈氏宗谱）

基于 Python3 的屈氏宗谱与文化平台，仅对外展示屈氏相关；**系统保留多姓氏接口**，可添加或切换其他姓氏族谱。采用 Flask+SQLite 架构，非前后端分离，部署简单、易二次开发。

## 功能概览

- **公开页面（无需登录）**：门户首页、族谱库列表、族谱详情（谱籍与字辈摘要）、屈氏文化。
- **需登录后查看**：成员列表、世系树、成员查询与亲属关系、族谱/成员/字辈的新增与编辑。
- **姓名脱敏**：成员、树形、查询结果中姓名仅显示前两字与后两字，中间以 * 代替。
- **屈氏文化**：屈姓起源、郡望堂号、屈氏文化研究会（参考 [ly-web](https://github.com/quxiangshun/ly-web)）。

## 部署说明

1. **环境**：Python 3.x，安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. **启动**：在项目根目录执行
   ```bash
   python app.py
   ```
   访问 <http://127.0.0.1:5000/> 或 <http://服务器IP:5000/>
3. **生产部署**：将 `config.py` 中 `DEBUG = False`，建议使用 Gunicorn：
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
4. **数据**：SQLite 数据库文件为项目根目录下 `genealogy.db`，首次运行自动创建。

5. **登录**：管理账号由环境变量 `ADMIN_USERNAME`、`ADMIN_PASSWORD` 控制，默认均为 `admin`。部署时请设置强密码，例如：`set ADMIN_PASSWORD=你的密码`（Windows）或 `export ADMIN_PASSWORD=你的密码`（Linux）。

6. **公开族谱入库**：执行 `python -m scripts.seed_public_genealogies` 入库江苏常熟、湖北秭归、湖南溆浦、屈氏河东、**陕西渭南屈氏族谱（屈仲辉提供）** 等。重复执行不会重复插入同名族谱。

7. **根据 docs 完善屈氏信息与人员**：若已将《屈氏族谱（陕西渭南屈仲辉提供）.doc》等放入 `docs/`，可先提取文本再入库人员：
   ```bash
   python -m scripts.extract_doc_text   # 从 .doc 提取 txt（需 pip install olefile）
   python -m scripts.import_from_docs    # 创建陕西渭南族谱并添加成员屈仲辉（资料提供者）
   ```
   屈氏文化页的「名人举例」「各地字辈摘录」已据 docs 内容整理，详见 `docs/README.md`。

8. **族谱网四本录入**：将 [zupu.cn](https://www.zupu.cn/) 上四本屈氏族谱的谱籍信息、字辈与始祖成员录入系统：
   ```bash
   python -m scripts.import_zupu_genealogies
   ```
   对应链接：215148 临海屈氏世谱、46475 敦睦堂屈氏宗谱、103834 雙峰屈氏五修宗譜、103835 湘鄉屈氏四修宗譜。脚本会创建或更新这四条族谱、为敦睦堂录入 24 字字辈、为各谱录入始祖成员。
