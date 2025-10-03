/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PermissionDto } from '../models/PermissionDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class PermissionsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Permissions
   * @returns PermissionDto Successful Response
   * @throws ApiError
   */
  public getPermissionsApiV1PermissionsGet(): CancelablePromise<Array<PermissionDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/permissions/',
    });
  }
}
