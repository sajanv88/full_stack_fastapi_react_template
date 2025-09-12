/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StorageProvider } from './StorageProvider';
export type StorageSettings = {
  provider: StorageProvider;
  is_enabled: boolean;
  region: string;
  aws_access_key?: (string | null);
  aws_secret_key?: (string | null);
  aws_bucket_name?: (string | null);
  azure_connection_string?: (string | null);
  azure_container_name?: (string | null);
};

