/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuditLogDto } from './AuditLogDto';
export type AuditLogListDto = {
  total: number;
  logs: Array<AuditLogDto>;
  has_next: boolean;
  has_previous: boolean;
  limit: number;
  skip: number;
};

