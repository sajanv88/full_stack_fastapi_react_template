/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AiModel } from './AiModel';
import type { UserPreference } from './UserPreference';
export type AppConfigResponse = {
  is_multi_tenant_enabled: boolean;
  multi_tenancy_strategy: string;
  host_main_domain: string;
  available_ai_models?: (Array<AiModel> | null);
  is_user_logged_in?: (boolean | null);
  user_preferences?: (UserPreference | null);
};

