# annofab-task-assignment-plugin-sample
Annofabの[タスク割当プラグイン](https://annofab.readme.io/docs/oraganization-plugin-task-assignment)で利用できるWebAPIのサンプルです。

# 仕様
このWeb APIは、以下のルールでタスクを割り当てます。

* user_idがalice、bobのとき：メタデータのgroupキーがAのタスクを割り当てる
* user_idがcarol、daveのとき：メタデータのgroupキーがBのタスクを割り当てる


# Requirements
* poetry 2.1以上
* Python 3.12以上

# Install

```
$ poetry install
```

# 起動

```
$ poetry run uvicorn app.main:app
INFO:     Started server process [1459638]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 動作確認

```
$ curl --request 'OPTIONS' 'http://127.0.0.1:8000/tasks/assign' --verbose
*   Trying 127.0.0.1:8000...
* Connected to 127.0.0.1 (127.0.0.1) port 8000 (#0)
> OPTIONS /tasks/assign HTTP/1.1
> Host: 127.0.0.1:8000
> User-Agent: curl/7.81.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< date: Tue, 18 Feb 2025 05:48:18 GMT
< server: uvicorn
< access-control-allow-origin: https://annofab.com
< access-control-allow-headers: Content-Type
< content-length: 2
< content-type: application/json
<
* Connection #0 to host 127.0.0.1 left intact
```

