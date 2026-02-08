/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_logo_api_v1_brandings_logo_put } from '../models/Body_upload_logo_api_v1_brandings_logo_put';
import type { UpdateBrandingDto } from '../models/UpdateBrandingDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class BrandingService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Update Branding
   * @returns void
   * @throws ApiError
   */
  public updateBrandingApiV1BrandingsPost({
    requestBody,
  }: {
    requestBody: UpdateBrandingDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/brandings/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Partial Update Branding
   * @returns void
   * @throws ApiError
   */
  public partialUpdateBrandingApiV1BrandingsBrandingIdPatch({
    brandingId,
    requestBody,
  }: {
    brandingId: string,
    requestBody: UpdateBrandingDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/brandings/{branding_id}',
      path: {
        'branding_id': brandingId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Upload Logo
   * @returns any Successful Response
   * @throws ApiError
   */
  public uploadLogoApiV1BrandingsLogoPut({
    formData,
  }: {
    formData: Body_upload_logo_api_v1_brandings_logo_put,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/brandings/logo',
      formData: formData,
      mediaType: 'multipart/form-data',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
