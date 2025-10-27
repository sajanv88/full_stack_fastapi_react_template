/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreatePricingDto } from '../models/CreatePricingDto';
import type { PricingListDto } from '../models/PricingListDto';
import type { UpdatePricingDto } from '../models/UpdatePricingDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripePricingService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Pricing List
   * @returns PricingListDto Successful Response
   * @throws ApiError
   */
  public getPricingListApiV1PricesGet(): CancelablePromise<PricingListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/prices/',
    });
  }
  /**
   * Create Pricing
   * @returns any Successful Response
   * @throws ApiError
   */
  public createPricingApiV1PricesPost({
    requestBody,
  }: {
    requestBody: CreatePricingDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/prices/',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Pricing
   * @returns void
   * @throws ApiError
   */
  public updatePricingApiV1PricesPriceIdPatch({
    priceId,
    requestBody,
  }: {
    priceId: string,
    requestBody: UpdatePricingDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/prices/{price_id}',
      path: {
        'price_id': priceId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
