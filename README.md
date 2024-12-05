# Shop-BE

## 部署方式 🛠️

必须拥有以下环境:

- Python 3.12+
- MySQL 服务器
- Poetry

安装依赖:

```bash
poetry install
```

如果在 Linux 下，必须先安装前置的 MySQL 依赖:

```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config # Debian / Ubuntu
```

```bash
sudo yum install python3-devel mysql-devel pkgconfig # Red Hat / CentOS
```

在程序根目录下创建一个`.env`文件，内容如下(请将花括号内内容替换为实际内容):

```env
SECRET_KEY={32位随机安全密钥}
DB_URL={数据库连接地址，包含URL和端口}
DB_NAME={数据库名}
DB_USER={数据库用户名}
DB_PASSWORD={数据库密码}
EMAIL_HOST={SMTP服务器地址}
EMAIL_PORT={SMTP服务器端口}
EMAIL_ADDR={邮箱地址}
EMAIL_PWD={邮箱密码}
LOG_LEVEL={日志级别, 可选项: DEBUG, INFO, WARNING, ERROR, CRITICAL，可不填}
```

安全密钥可使用以下命令生成(确保已安装`openssl`):

```bash
openssl rand -hex 32
```

程序会检测数据库内是否是初次运行，如果没有则会自动创建表。

默认用户注册时只有普通用户权限，如果需要添加管理员权限，请在数据库中手动修改用户权限。拥有一个管理员账号后，可以通过管理员账号添加其他管理员。

## 运行方式 🚀

```bash
poetry run uvicorn main:app
```

如果希望能使用热更新功能，可以使用以下命令:

```bash
poetry run uvicorn main:app --reload
```
