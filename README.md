# Java Manager

## 项目简介

Java Manager 是一个用于 Windows 平台的图形化 Java JDK版本环境管理工具，支持多版本 JDK/JRE 环境变量的添加、切换，自动配置 JAVA_HOME、Path 及 .jar 文件关联。

## 主要功能

- 支持添加多个 JDK/JRE 版本，支持 JDK 带/不带独立 JRE 目录
- 一键切换当前使用的 Java 版本（自动设置 JAVA_HOME）
- 自动检测并追加 Path 中的 `%JAVA_HOME%\bin`（只追加一次）
- 切换时自动将 .jar 文件关联到当前 JDK/JRE 的 javaw.exe
- 所有配置持久化保存，重启后自动加载
- 简洁直观的图形界面

## 环境要求

- Windows 10/11
- Python 3.7 及以上
- 需以管理员权限运行（涉及系统环境变量和注册表操作）

## 安装与运行

1. 安装 Python 3（推荐 3.7 及以上）

2. 安装依赖（标准库，无需额外第三方包）

3. 下载本项目源码

4. 以管理员身份运行：

   ```shell
   python java-manager.py
   ```

## 使用说明

### 添加 Java 版本

1. 点击“添加 Java 版本”按钮，选择 JDK 目录
<img width="1258" height="789" alt="image" src="https://github.com/user-attachments/assets/37a00461-ecbb-4fef-bbfb-919fc27584be" />

2. 输入版本号（如 jdk8、jdk11）
<img width="773" height="480" alt="image" src="https://github.com/user-attachments/assets/9a3f5c81-e2ec-4768-802d-bb7ffb1fac80" />

3. 若有独立 JRE 目录，选择“是”并指定 JRE 目录，否则选择“否”
<img width="777" height="266" alt="image" src="https://github.com/user-attachments/assets/e8d33cc0-bb1f-4749-834a-cf0b4656a33f" />
<img width="1258" height="789" alt="image" src="https://github.com/user-attachments/assets/c12cfda5-c578-4575-aa85-557ed8b2f5a4" />

4. 添加后会在列表中显示 JDK 和 JRE 路径
<img width="773" height="480" alt="image" src="https://github.com/user-attachments/assets/79baece4-4d93-48f7-b813-fbf93f5d9c74" />

### 切换 Java 版本（.jar自动关联，支持不同版本兼容jar包双击打开）

1. 在列表中选择要切换的版本
2. 点击“切换到选中版本”按钮
3. 程序会自动：
   - 设置 JAVA_HOME
   - 检查并追加 Path 中的 `%JAVA_HOME%\bin`
   - 修改 .jar 文件关联到当前 JDK/JRE 的 javaw.exe

### 删除 管理的Java JDK版本目录

- 选中列表中的版本，点击“删除选中版本”即可

## 注意事项

- **必须以管理员身份运行**，否则无法修改系统环境变量和注册表
- Path 只会自动追加 `%JAVA_HOME%\bin` 一次，后续切换无需重复追加
- .jar 文件关联会被自动同步到当前 JDK/JRE 的 javaw.exe
- JDK/JRE 路径建议全英文、无空格、无特殊字符

## 常见问题

**Q: 切换后 .jar 文件无法双击运行？**

- 请检查注册表 `HKEY_CLASSES_ROOT\jarfile\shell\open\command` 的值是否为：

  ```
  "JDK或JRE路径\\bin\\javaw.exe" -jar "%1" %*
  ```

- 确认 javaw.exe 路径无误，且有执行权限

- 确认已以管理员身份运行本程序

**Q: Path 变量被截断或异常？**

- Path 变量过长时，setx 可能导致截断。建议提前备份 Path。

**Q: JDK/JRE 路径有中文或特殊字符，导致无法运行？**

- 建议将 JDK/JRE 安装在全英文路径下

## 许可信息

本项目基于 MIT License 开源，欢迎自由使用与修改。 
