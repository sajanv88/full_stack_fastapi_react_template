/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type AuditLogDto = {
  entity: string;
  action: 'create' | 'update' | 'delete' | 'read' | 'login' | 'logout';
  changes?: Record<string, any>;
  user_id: string;
  timestamp?: string;
  tenant_id?: (string | null);
};

