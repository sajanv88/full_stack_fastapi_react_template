from collections import deque
import glob
import json
from typing import List
from api.common.utils import capture_audit_log, get_logger
from api.domain.dtos.audit_logs_dto import AuditLogDto, AuditLogListDto

logger = get_logger(__name__)

class AuditLogRepository:
    async def add_audit_log(self, audit_log: AuditLogDto) -> None:
        await capture_audit_log(audit_log)

    async def list_audit_logs(self, tenant_id: str | None = None, limit: int = 10, skip: int = 0) -> AuditLogListDto:
        file_path_pattern = "/tmp/audit_logs_forhost_*.jsonl"
        if tenant_id:
            file_path_pattern = f"/tmp/audit_logs_for{tenant_id}_*.jsonl"

        logger.info(f"Reading audit logs from files matching pattern: {file_path_pattern}")

        files = glob.glob(file_path_pattern)

        # IMPORTANT: scan oldest → newest so the deque ends up with the last K lines
        # If your filenames end with YYYY-MM-DD, name sort works for chronological asc.
        files.sort()  # ascending

        total = 0
        keep = skip + limit
        ring = deque(maxlen=keep) # keep the last (skip + limit) lines

        for file_path in files:
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        total += 1
                        ring.append(line)  # older ones drop automatically when full
            except FileNotFoundError:
                continue

        # Now ring holds the last (skip+limit) lines globally (latest lines overall)
        # Convert to newest-first
        newest_first = list(ring)[::-1]

        # Slice for pagination
        lines = newest_first[skip:skip + limit]

        # Parse JSON and map to DTOs
        logs: List[AuditLogDto] = [AuditLogDto(**json.loads(l)) for l in lines]

        return AuditLogListDto(
            total=total,
            logs=logs,
            has_next=(skip + limit) < total,
            has_previous=skip > 0,
            limit=limit,
            skip=skip
        )
