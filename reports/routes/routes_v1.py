from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database_async import get_async_session
from reports.models.models_v1 import UserReport, LLMReport

from reports.schemas.schemas_v1 import (
    UserReportCreate,
    UserReportUpdate,
    UserReportOut,
    LLMReportOut,
)
from core.authentication import get_current_user
from users.models.models_v1 import User

router = APIRouter(
    prefix="/reports/",
    tags=["Reports"]
)


@router.post("/user-reports", response_model=UserReportOut)
async def create_user_report(
    payload: UserReportCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    report = UserReport(
        text=payload.text,
        task_id=payload.task_id,
        user_id=current_user.id,
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report


@router.put("/user-reports/{report_id}", response_model=UserReportOut)
async def update_user_report(
    report_id: UUID,
    payload: UserReportUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    report = await session.get(UserReport, report_id)

    if not report:
        raise HTTPException(404, "Report not found")

    if report.user_id != current_user.id:
        raise HTTPException(403, "Not your report")

    if report.is_verified:
        raise HTTPException(400, "Verified report cannot be updated")

    report.text = payload.text
    report.task_id = payload.task_id

    await session.commit()
    await session.refresh(report)
    return report

@router.post("/user-reports/{report_id}/send")
async def send_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    report = await session.get(UserReport, report_id)

    if not report:
        raise HTTPException(status_code=404, detail="Report tapılmadı")

    # TEAM MEMBER LOGIC
    if current_user.role == "team_member":
        if report.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Bu report sizə aid deyil")

        if report.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Təsdiqlənmiş report yenidən göndərilə bilməz"
            )

        report.is_sent_teamlead = True

    # TEAM LEAD LOGIC
    elif current_user.role == "team_lead":
        if not report.is_verified:
            raise HTTPException(
                status_code=400,
                detail="Təsdiqlənməmiş report göndərilə bilməz"
            )

        report.is_sent_po = True

    else:
        raise HTTPException(
            status_code=403,
            detail="Bu rol üçün icazə yoxdur"
        )

    await session.commit()

    return {"status": "Report uğurla göndərildi"}


@router.patch("/user-reports/{report_id}/verify")
async def verify_user_report(
    report_id: UUID,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "team_lead":
        raise HTTPException(403, "Yalnız team leader dəyişə bilər")

    report = await session.get(UserReport, report_id)

    if not report:
        raise HTTPException(404, "Report not found")

    report.is_verified = True
    await session.commit()

    return {"status": "verified"}

