/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SSOProvider } from './SSOProvider';
export type ReadSSOSettingsDto = {
  enabled: boolean;
  provider: SSOProvider;
  client_id: string;
  client_secret?: (string | null);
  id: string;
};

