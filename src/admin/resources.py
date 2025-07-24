import os
from typing import List

from fastapi_admin.app import app
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.resources import Action, Dropdown, Field, Link, Model, ToolbarAction
from fastapi_admin.widgets import displays, filters, inputs
from starlette.requests import Request

from src.constants import BASE_DIR
from src.models import Admin, MonitoredMetric, Sla

upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


@app.register
class Dashboard(Dropdown):
    label = "Relatórios"
    icon = "fas fa-chart-bar"
    url = "/admin/report"

    class Overview(Link):
        label = "Report geral"
        icon = "fas fa-chart-bar"
        url = "/admin"

    class SLAReport(Link):
        label = "SLA Report"
        icon = "fas fa-chart-line"
        url = "/admin/sla/report"
        filters = [
            filters.Search(
                name="metric__name",
                label="Métrica",
                search_mode="contains",
                placeholder="Search for metric name",
            ),
        ]

    class DependencyList(Link):
        label = "Dependências"
        icon = "fas fa-plug"
        url = "/admin/dependencies"
     
    resources = [Overview, SLAReport, DependencyList]


@app.register
class AdminResource(Model):
    label = "Usuários"
    model = Admin
    icon = "fas fa-user"
    page_pre_title = "admin list"
    page_title = "admin model"
    filters = [
        filters.Search(
            name="username",
            label="Name",
            search_mode="contains",
            placeholder="Search for username",
        ),
        filters.Date(name="created_at", label="CreatedAt"),
    ]
    fields = [
        "id",
        "username",
        Field(
            name="password",
            label="Password",
            display=displays.InputOnly(),
            input_=inputs.Password(),
        ),
        Field(name="email", label="Email", input_=inputs.Email()),
        Field(
            name="avatar",
            label="Avatar",
            display=displays.Image(width="40"),
            input_=inputs.Image(null=True, upload=upload),
        ),
        "created_at",
    ]

    async def get_toolbar_actions(self, request: Request) -> List[ToolbarAction]:
        return []

    async def cell_attributes(self, request: Request, obj: dict, field: Field) -> dict:
        if field.name == "id":
            return {"class": "bg-danger text-white"}
        return await super().cell_attributes(request, obj, field)

    async def get_actions(self, request: Request) -> List[Action]:
        return []

    async def get_bulk_actions(self, request: Request) -> List[Action]:
        return []


@app.register
class Content(Dropdown):
    class MonitoredMetricResource(Model):
        label = "Métricas"
        model = MonitoredMetric
        fields = [
            "id",
            "name",
            "unit",
            "is_active",
            "created_at",
        ]
        filters = [
            filters.Search(
                name="name",
                label="Name",
                search_mode="contains",
                placeholder="Search for metric name",
            )        
        ]

    class SLAResource(Model):
        label = "Definição de SLA"
        model = Sla
        fields = [
            "id",
            Field(
                name="metric_id",
                label="Métrica",
                input_=inputs.ForeignKey(
                    model=MonitoredMetric
                ),
            ),
            "min_threshold",
            "max_threshold",
            "is_active",
            "created_at",
        ]
        filters = [
            filters.Search(
                name="metric__name",
                label="Métrica",
                search_mode="contains",
                placeholder="Search for metric name",
            )
        ]

    label = "Configuração"
    icon = "fas fa-cogs"
    resources = [SLAResource, MonitoredMetricResource]


@app.register
class GithubLink(Link):
    label = "Github"
    url = "https://github.com/lucasousa/cloud-sentinel"
    icon = "fab fa-github"
    target = "_blank"
