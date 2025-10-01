/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AIHistoriesDto } from './AIHistoriesDto';
export type AISessionByUserIdDto = {
  id: string;
  session_id: string;
  created_at: string;
  history_id: string;
  tenant_id?: (string | null);
  user_id: string;
  sessions: Array<AIHistoriesDto>;
};

