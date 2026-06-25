from app.domain.entities.scrape_job import ScrapeJob
from app.domain.entities.scrape_result import ScrapeResult
from app.domain.enums import ScrapeStatus
from app.infrastructure.db.scrape_job_model import ScrapeJobModel
from app.infrastructure.db.scrape_result_model import ScrapeResultModel


def job_to_entity(m: ScrapeJobModel) -> ScrapeJob:
    return ScrapeJob(
        id=m.id,
        source_id=m.source_id,
        status=ScrapeStatus(m.status),
        celery_task_id=m.celery_task_id,
        started_at=m.started_at,
        completed_at=m.completed_at,
        opportunities_found=m.opportunities_found,
        opportunities_new=m.opportunities_new,
        error_message=m.error_message,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def job_to_model(e: ScrapeJob) -> ScrapeJobModel:
    return ScrapeJobModel(
        id=e.id,
        source_id=e.source_id,
        status=str(e.status),
        celery_task_id=e.celery_task_id,
        started_at=e.started_at,
        completed_at=e.completed_at,
        opportunities_found=e.opportunities_found,
        opportunities_new=e.opportunities_new,
        error_message=e.error_message,
    )


def apply_job_to_model(e: ScrapeJob, m: ScrapeJobModel) -> None:
    m.status = str(e.status)
    m.celery_task_id = e.celery_task_id
    m.started_at = e.started_at
    m.completed_at = e.completed_at
    m.opportunities_found = e.opportunities_found
    m.opportunities_new = e.opportunities_new
    m.error_message = e.error_message


def result_to_entity(m: ScrapeResultModel) -> ScrapeResult:
    return ScrapeResult(
        id=m.id,
        scrape_job_id=m.scrape_job_id,
        raw_url=m.raw_url,
        fingerprint=m.fingerprint,
        opportunity_id=m.opportunity_id,
        was_duplicate=m.was_duplicate,
        was_rejected=m.was_rejected,
        rejection_reason=m.rejection_reason,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def result_to_model(e: ScrapeResult) -> ScrapeResultModel:
    return ScrapeResultModel(
        id=e.id,
        scrape_job_id=e.scrape_job_id,
        raw_url=e.raw_url,
        fingerprint=e.fingerprint,
        opportunity_id=e.opportunity_id,
        was_duplicate=e.was_duplicate,
        was_rejected=e.was_rejected,
        rejection_reason=e.rejection_reason,
    )
