import annofabapi.credentials
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from fastapi import status
import annofabapi
from typing import Any

app = FastAPI()


class RequestBody(BaseModel):
    authorization_token: str
    """タスク割当専用の認証トークン。AnnofabのAPIを利用する際に使用します。"""
    project_id: str
    """タスクの割当リクエストが行われたプロジェクトのID"""
    phase: str
    """ユーザーが割当を要求したタスクのフェーズ。このフェーズのタスクを割当してください。"""


class AnnofabFacade:
    def __init__(self, authorization_token: str, project_id: str):
        self.annofab_service = annofabapi.build()
        self.project_id = project_id

        # 適当な文字列でuser_idとpasswordは不要なので適当な文字列を設定する
        annofab_service = annofabapi.build(login_user_id="***", login_password="***")
        # access_tokenとrefresh_tokenは不要なので、空文字で設定する
        annofab_service.api.tokens = annofabapi.credentials.Tokens(
            id_token=authorization_token, access_token="", refresh_token=""
        )
        self.annofab_service = annofab_service

    def get_user_id(self) -> str:
        my_account, _ = self.annofab_service.api.get_my_account()
        return my_account["user_id"]

    def get_task_id_for_assignee(self, task_phase: str, user_id: str) -> str | None:
        """
        ユーザー`user_id`に割り当てるタスクのIDを取得する
        alice,bobはグループA、carol,daveはグループBのタスクを割り当てる。
        """
        group: str | None = None
        match user_id:
            case "alice" | "bob":
                group = "A"
            case "carol" | "dave":
                group = "B"
            case _:
                return None

        assert group is not None

        # メタデータの`group`キーで絞り込む
        # タスクの更新日時が最も新しいタスクを取得する
        content, _ = self.annofab_service.api.get_tasks(
            self.project_id,
            query_params={
                "phase": task_phase,
                "no_user": True,
                "metadata": f"group:{group}",
                "sort": "-updated_datetime",
            },
        )
        task_list = content["list"]
        if len(task_list) > 0:
            return task_list[0]["task_id"]
        return None

    def assign_task(self, task_id: str, user_id: str) -> dict[str, Any]:
        """
        ユーザー`user_id`に、タスク`task_id`を割り当てる

        Returns:
            割り当てたタスクの情報

        """
        request_body = {
            "request_type": {
                "user_id": user_id,
                "task_ids": [task_id],
                "_type": "Selection",
            },
        }
        assigned_tasks, _ = self.annofab_service.api.assign_tasks(
            self.project_id, request_body=request_body
        )
        return assigned_tasks[0]


@app.post("/tasks/assign")
def assign_task(body: RequestBody) -> JSONResponse:
    response_headers = {"Access-Control-Allow-Origin": "https://annofab.com"}

    facade = AnnofabFacade(
        authorization_token=body.authorization_token, project_id=body.project_id
    )

    user_id = facade.get_user_id()
    task_id = facade.get_task_id_for_assignee(task_phase=body.phase, user_id=user_id)

    if task_id is not None:
        assigned_task = facade.assign_task(task_id=task_id, user_id=user_id)
        return JSONResponse(
            content=assigned_task,
            headers=response_headers,
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"errors": [{"error_code": "MISSING_RESOURCE"}]},
        headers=response_headers,
        status_code=status.HTTP_404_NOT_FOUND,
    )


@app.options("/tasks/assign", status_code=status.HTTP_200_OK)
def assign_task_preflight() -> JSONResponse:
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "https://annofab.com",
            "Access-Control-Allow-Headers": "Content-Type",
        },
    )
