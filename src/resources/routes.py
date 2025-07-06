from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from fastapi_admin.app import app
from fastapi_admin.app import app as admin_app
from fastapi_admin.depends import get_current_admin, get_resources
from fastapi_admin.template import templates


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
