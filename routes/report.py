from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

report_router = APIRouter(
    prefix="/report",
    tags=["report"],
)


class ReportData(BaseModel):
    server_port: Optional[str] = None
    server_ip: Optional[str] = None
    reported_ip: Optional[str] = None
    reported_uuid: Optional[str] = None
    reporting_nick: Optional[str] = None
    auth: Optional[str] = None
    reported_username: Optional[str] = None
    report_reason: Optional[str] = None


@report_router.post("/")
async def report(request: Request):
    try:
        form_data = await request.form()
        print("Received form data:", form_data)

        report_data = ReportData(
            server_port=form_data.get("server-port"),
            server_ip=form_data.get("server-ip"),
            reported_ip=form_data.get("reported-ip"),
            reported_uuid=form_data.get("reported-uuid"),
            reporting_nick=form_data.get("reporting-nick"),
            auth=form_data.get("auth"),
            reported_username=form_data.get("reported-username"),
            report_reason=form_data.get("report-reason")
        )

        print("Processed report data:", report_data.dict())

        return {"status": "ok"}
    except Exception as e:
        raise e