import httpx
from fastapi import Depends, Request
from fastapi_admin.app import app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates

from src.admin.query import (
    aggregate_by_time_slice,
    aggregate_metrics,
    metrics_by_dependence,
)
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


@app.get("/sla/report_by_dependence/{dependence}", name="sla_report_by_dependence")
async def report_by_dependence(
    request: Request,
    resources=Depends(get_resources),
    dependence: str = ""
):
    sla_reports = await metrics_by_dependence(dependence=dependence)
    for r in sla_reports:
        if 'timestamp' in r and r['timestamp']:
            r['timestamp'] = r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    return templates.TemplateResponse(
        "sla_report_by_dependence.html",
        context={
            "request": request,
            "resources": resources,
            "sla_reports": sla_reports,
            "resource_label": "SLA Report",
            "page_pre_title": "list",
            "page_title": "SLA Report List",
        },
    )