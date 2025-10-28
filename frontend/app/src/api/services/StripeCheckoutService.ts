/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BillingRecordListDto } from '../models/BillingRecordListDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripeCheckoutService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Create Checkout Session
   * @returns any Successful Response
   * @throws ApiError
   */
  public createCheckoutSessionApiV1CheckoutsHostPost(): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/checkouts/host',
    });
  }
  /**
   * List Checkout Records
   * @returns BillingRecordListDto Successful Response
   * @throws ApiError
   */
  public listCheckoutRecordsApiV1CheckoutsAllGet({
    skip,
    limit = 100,
  }: {
    skip?: number,
    limit?: number,
  }): CancelablePromise<BillingRecordListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/checkouts/all',
      query: {
        'skip': skip,
        'limit': limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
