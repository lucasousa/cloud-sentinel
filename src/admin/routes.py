import httpx
from fastapi import Depends, Request
from fastapi_admin.app import app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates

from src.admin.query import aggregate_by_time_slice, aggregate_metrics
from src.classifier.utils import classify_full_metrics, get_sla_values
from src.models import Dependencies, MonitoringAggregationTime


@app.get("/")
async def home(
    request: Request,
    resources=Depends(get_resources),
):
    async def make_request():
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/get")
            print("Status code:", response.status_code)
            print("Response body:", response.text)
    await make_request()
    report = await aggregate_metrics()
    sla = await get_sla_values()
    for index in report:
        index["status"] = classify_full_metrics(
            {
                "cpu_usage": index["cpu"],
                "memory_usage": index["memory"],
                "availability": index["availability"],
                "response_time": index["response_time"],
                "rtt": index["rtt"],
                "latency": index["latency"],
            },
            sla,
        )

    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "report": report,
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
    time_slice = await MonitoringAggregationTime.first()
    sla_reports = await aggregate_by_time_slice(
        interval=time_slice.window_size, unit=time_slice.window_unit
    )
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
