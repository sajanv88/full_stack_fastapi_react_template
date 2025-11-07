import glob
import json
from typing import List
from api.common.utils import get_logger
from api.domain.dtos.audit_logs_dto import AuditLogDto, AuditLogListDto

logger = get_logger(__name__)

class AuditLogsService:

    async def read_audit_logs(self, limit: int, skip: int) -> AuditLogListDto:
    
        results: List[AuditLogDto] = []
        total = 0
        collected_logs = 0
        try:
            files = glob.glob('/tmp/audit_logs_*.jsonl')
            logger.info(f"Found audit log files: {files}")
            if not files:
                raise FileNotFoundError("No audit log files found.")
            files.sort(reverse=True)
            for file_path in files:
                filename = file_path
                with open(filename, 'r') as file:
                    for line in file:
                        total += 1
                        if total <= skip:
                            continue
                        
                        if collected_logs < limit:
                            log = json.loads(line)
                            results.append(AuditLogDto(**log))
                            collected_logs += 1
                        else:
                            break
                if collected_logs >= limit:
                    break
            return AuditLogListDto(
                total=total,
                logs=results,
                has_next=skip + limit < total,
                has_previous=skip > 0,
                limit=limit,
                skip=skip
            )
        except FileNotFoundError as e:
            logger.error(f"Audit log file not found: {e}")
            return AuditLogListDto(total=0, logs=[], has_next=False, has_previous=False, limit=limit, skip=skip)


    async def generate_audit_logs_download(self) -> None:
        # Placeholder implementation
        return None