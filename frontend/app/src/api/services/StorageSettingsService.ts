/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AvailableStorageProviderDto } from '../models/AvailableStorageProviderDto';
import type { StorageSettingsDto } from '../models/StorageSettingsDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StorageSettingsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Storage Settings
   * @returns AvailableStorageProviderDto Successful Response
   * @throws ApiError
   */
  public getStorageSettingsApiV1StorageGet(): CancelablePromise<Array<AvailableStorageProviderDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/storage/',
    });
  }
  /**
   * Get Available Providers
   * @returns string Successful Response
   * @throws ApiError
   */
  public getAvailableProvidersApiV1StorageAvailableGet(): CancelablePromise<Array<Record<string, string>>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/storage/available',
    });
  }
  /**
   * Configure Storage
   * @returns any Successful Response
   * @throws ApiError
   */
  public configureStorageApiV1StorageConfigurePost({
    requestBody,
  }: {
    requestBody: StorageSettingsDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/storage/configure',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Reset Storage
   * @returns void
   * @throws ApiError
   */
  public resetStorageApiV1StorageStorageIdResetPatch({
    storageId,
  }: {
    storageId: string,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/storage/{storage_id}/reset',
      path: {
        'storage_id': storageId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
