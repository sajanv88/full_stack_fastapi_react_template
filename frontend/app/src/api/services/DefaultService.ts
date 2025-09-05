/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DefaultService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Serve React App
   * @returns any Successful Response
   * @throws ApiError
   */
  public serveReactAppGet(): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/',
    });
  }
  /**
   * React Router
   * @returns any Successful Response
   * @throws ApiError
   */
  public reactRouterFullPathGet({
    fullPath,
  }: {
    fullPath: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/{full_path}',
      path: {
        'full_path': fullPath,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
