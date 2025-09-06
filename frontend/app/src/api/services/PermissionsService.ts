/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PermissionBase } from '../models/PermissionBase';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class PermissionsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Permissions
   * @returns PermissionBase Successful Response
   * @throws ApiError
   */
  public getPermissionsApiV1PermissionsGet(): CancelablePromise<Array<PermissionBase>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/permissions/',
    });
  }
}
