/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type StorageSettingsDto = {
  provider: 's3' | 'azure_blob';
  is_enabled: boolean;
  region: string;
  aws_access_key?: (string | null);
  aws_secret_key?: (string | null);
  aws_bucket_name?: (string | null);
  azure_connection_string?: (string | null);
  azure_container_name?: (string | null);
  updated_by_user_id?: (string | null);
};

