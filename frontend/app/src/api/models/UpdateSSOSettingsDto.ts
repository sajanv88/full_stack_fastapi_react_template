/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type UpdateSSOSettingsDto = {
  enabled?: (boolean | null);
  provider?: ('google' | 'github' | 'discord' | 'microsoft' | 'linkedin' | 'x' | 'notion' | 'gitlab' | 'bitbucket' | 'facebook' | null);
  client_id?: (string | null);
  client_secret?: (string | null);
  scopes?: (Array<string> | null);
};

