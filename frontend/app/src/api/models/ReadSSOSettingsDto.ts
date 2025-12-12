/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type ReadSSOSettingsDto = {
  enabled: boolean;
  provider: 'google' | 'github' | 'discord' | 'microsoft' | 'linkedin' | 'x' | 'notion' | 'gitlab' | 'bitbucket' | 'facebook';
  client_id: string;
  client_secret?: (string | null);
  scopes?: (Array<string> | null);
  redirect_uris?: (Array<string> | null);
  id: string;
};

