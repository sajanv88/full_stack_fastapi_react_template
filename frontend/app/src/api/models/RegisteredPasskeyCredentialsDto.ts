/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AuthenticatorTransport } from './AuthenticatorTransport';
export type RegisteredPasskeyCredentialsDto = {
  credential_id: string;
  public_key: string;
  sigin_count: number;
  transports?: Array<AuthenticatorTransport>;
  created_at: string;
  last_used_at?: (string | null);
};

