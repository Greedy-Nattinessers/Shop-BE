# Shop-BE

[![Tests](https://github.com/Greedy-Nattinessers/Shop-BE/actions/workflows/test.yml/badge.svg)](https://github.com/Greedy-Nattinessers/Shop-BE/actions/workflows/test.yml)

[![codecov](https://codecov.io/gh/Greedy-Nattinessers/Shop-BE/graph/badge.svg?token=1FLZ0YFMSS)](https://codecov.io/gh/Greedy-Nattinessers/Shop-BE)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Greedy-Nattinessers_Shop-BE&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Greedy-Nattinessers_Shop-BE)

## 最近一次的测试覆盖

![coverage](https://codecov.io/gh/Greedy-Nattinessers/Shop-BE/graphs/sunburst.svg?token=1FLZ0YFMSS)

## 部署方式 🛠️

必须拥有以下环境:

- `Python` 3.12+
- `MySQL` 服务器
- `uv`

安装指定的 Python 版本:

```bash
uv python install
```

如果在 Linux 下，必须先安装前置的 MySQL 客户端依赖:

```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config # Debian / Ubuntu
```

```bash
sudo yum install python3-devel mysql-devel pkgconfig # Red Hat / CentOS
```

安装项目依赖:

```bash
uv sync
```

如果是在开发环境下需要运行测试代码，可以使用以下命令安装开发环境下的依赖:

```bash
uv sync --dev
```

修改`Services/Config/config.toml.sample`中的相应配置信息并保存为`config.toml`:

程序会检测数据库内是否是初次运行，如果没有则会自动创建数据库中的各表结构。

**第一个注册的用户会被自动设置为管理员**，但删除到最后一个用户时不会将其设置为管理员。

## 运行方式 🚀

如果是调试 FastAPI 服务，可以使用以下命令:

```bash
uv run fastapi dev
```

部署，推荐使用 `Docker` 来完成。
