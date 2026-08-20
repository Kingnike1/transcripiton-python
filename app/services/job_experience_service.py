"""Translate durable job state into safe, user-facing processing experience."""

from datetime import timezone
from typing import Protocol

from app.core.enums import JobStatus
from app.core.time import utc_now
from app.models.processing_job import ProcessingJob
from app.services.worker_heartbeat import WorkerHeartbeat


class HeartbeatReader(Protocol):
    def age_seconds(self) -> float | None: ...


_STATUS_LABELS = {
    JobStatus.PENDING.value: "Aguardando na fila",
    JobStatus.RUNNING.value: "Processando",
    JobStatus.RETRYING.value: "Tentando novamente",
    JobStatus.COMPLETED.value: "Concluído",
    JobStatus.FAILED.value: "Não foi possível concluir",
    JobStatus.CANCELLED.value: "Cancelado",
}


class JobExperienceService:
    """Derive UX state without changing the durable job source of truth."""

    def __init__(self, heartbeat: HeartbeatReader | None = None) -> None:
        self.heartbeat = heartbeat or WorkerHeartbeat()

    def describe(self, job: ProcessingJob) -> dict[str, object]:
        effective_status = job.status
        status_label = _STATUS_LABELS.get(job.status, job.status)
        next_action: str | None = None
        blocked_reason: str | None = None

        if job.status in {JobStatus.PENDING.value, JobStatus.RETRYING.value}:
            worker_age = self.heartbeat.age_seconds()
            if worker_age is None or worker_age > 15:
                effective_status = "BLOCKED"
                status_label = "Bloqueado por configuração"
                blocked_reason = "O Worker não está ativo ou não envia heartbeat recente."
                next_action = "Inicie ou reinicie o Worker e tente novamente."
            elif job.status == JobStatus.PENDING.value:
                next_action = "Aguarde o Worker iniciar o processamento."
            else:
                next_action = "Aguarde a próxima tentativa automática."
        elif job.status == JobStatus.RUNNING.value:
            next_action = "O processamento está em andamento."
        elif job.status == JobStatus.FAILED.value:
            next_action = "Revise o diagnóstico e use Tentar novamente."
        elif job.status == JobStatus.CANCELLED.value:
            next_action = "Inicie o processamento novamente quando desejar."

        reference = job.heartbeat_at or job.updated_at or job.created_at
        seconds_since_update: int | None = None
        if reference is not None:
            if reference.tzinfo is None:
                reference = reference.replace(tzinfo=timezone.utc)
            seconds_since_update = max(0, int((utc_now() - reference).total_seconds()))

        stalled = (
            job.status == JobStatus.RUNNING.value
            and seconds_since_update is not None
            and seconds_since_update > 90
        )
        if stalled:
            status_label = "Processamento sem atualização recente"
            next_action = "Verifique o Worker; o job pode ser recuperado automaticamente pelo lease."

        return {
            "effective_status": effective_status,
            "status_label": status_label,
            "next_action": next_action,
            "blocked_reason": blocked_reason,
            "seconds_since_update": seconds_since_update,
            "stalled": stalled,
            "can_cancel": job.status in {JobStatus.PENDING.value, JobStatus.RETRYING.value},
            "can_retry": job.status == JobStatus.FAILED.value,
        }
