/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SSOProvider } from './SSOProvider';
export type CreateSSOSettingsDto = {
  enabled: boolean;
  provider: SSOProvider;
  client_id: string;
  client_secret?: (string | null);
  scopes?: (Array<string> | null);
  tenant_id?: (string | null);
};

