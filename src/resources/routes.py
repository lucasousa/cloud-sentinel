import httpx
from fastapi import Depends, Request
from fastapi_admin.app import app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates

from src.models import Dependencies, SLAReport


@app.get("/")
async def home(
    request: Request,
    resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard",
        },
    )


@app.get("/report")
async def admin_dashboard(
    request: Request,
    resources=Depends(get_resources),
):
    # Simule ou consulte o relatório real aqui
    metric_reports = [
        {
            "provider_name": "AWS",
            "service_name": "EC2",
            "metrics": [
                {"name": "CPU", "value": 72.1, "unit": "%"},
                {"name": "Memory", "value": 64.0, "unit": "%"},
            ],
        },
        {
            "provider_name": "Azure",
            "service_name": "Functions",
            "metrics": [
                {"name": "Availability", "value": 0.999, "unit": ""},
                {"name": "Response Time", "value": 1.23, "unit": "s"},
            ],
        },
    ]
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "metric_reports": metric_reports,
        },
    )


@app.get("/dependencies")
async def list_dependencies(
    request: Request,
    resources=Depends(get_resources),
):
    dependencies = await Dependencies.all().order_by("name")
    return templates.TemplateResponse(
        "dependencies.html",
        context={
            "request": request,
            "resources": resources,
            "dependencies": dependencies,
            "resource_label": "Dependencies",
            "page_pre_title": "list",
            "page_title": "Dependencies List",
        },
    )


@app.get("/sla/report")
async def sla_report(
    request: Request,
    resources=Depends(get_resources),
):
    sla_reports = await SLAReport.all().prefetch_related("dependency").order_by("-timestamp")
    return templates.TemplateResponse(
        "sla_report.html",
        context={
            "request": request,
            "resources": resources,
            "sla_reports": sla_reports,
            "resource_label": "SLA Report",
            "page_pre_title": "list",
            "page_title": "SLA Report List",
        },
    )