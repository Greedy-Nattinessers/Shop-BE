# Shop-BE

[![Tests](https://github.com/Greedy-Nattinessers/Shop-BE/actions/workflows/test.yml/badge.svg)](https://github.com/Greedy-Nattinessers/Shop-BE/actions/workflows/test.yml)

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

修改`Services/Config/config.toml.sample`中的相应配置信息并保存为`config.toml`:

程序会检测数据库内是否是初次运行，如果没有则会自动创建数据库中的各表结构。

**第一个注册的用户会被自动设置为管理员。**但删除到最后一个用户时不会将其设置为管理员。

## 运行方式 🚀

```bash
poetry run uvicorn main:app
```

如果希望能使用热更新功能，可以使用以下命令:

```bash
poetry run uvicorn main:app --reload
```
