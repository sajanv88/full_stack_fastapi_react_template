/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuditLogListDto } from '../models/AuditLogListDto';
import type { DownloadResponseDto } from '../models/DownloadResponseDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuditLogsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List Audit Logs
   * @returns AuditLogListDto Successful Response
   * @throws ApiError
   */
  public listAuditLogsApiV1AuditLogsGet({
    limit = 10,
    skip,
    action,
  }: {
    limit?: number,
    skip?: number,
    action?: ('create' | 'update' | 'delete' | 'read' | 'login' | 'logout' | 'error' | 'download' | null),
  }): CancelablePromise<AuditLogListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/audit-logs/',
      query: {
        'limit': limit,
        'skip': skip,
        'action': action,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Download Audit Logs
   * @returns DownloadResponseDto Successful Response
   * @throws ApiError
   */
  public downloadAuditLogsApiV1AuditLogsDownloadPost({
    action,
  }: {
    action?: ('create' | 'update' | 'delete' | 'read' | 'login' | 'logout' | 'error' | 'download' | null),
  }): CancelablePromise<DownloadResponseDto> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/audit-logs/download',
      query: {
        'action': action,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
