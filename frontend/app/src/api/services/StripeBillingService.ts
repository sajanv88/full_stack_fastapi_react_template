/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreatePlanDto } from '../models/CreatePlanDto';
import type { InvoiceListDto } from '../models/InvoiceListDto';
import type { PlanDto } from '../models/PlanDto';
import type { PlanListDto } from '../models/PlanListDto';
import type { UpdatePlanDto } from '../models/UpdatePlanDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class StripeBillingService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * List available plans
   * @returns PlanListDto Successful Response
   * @throws ApiError
   */
  public listPlansApiV1BillingPlansGet(): CancelablePromise<PlanListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/billing/plans',
    });
  }
  /**
   * Retrieve a plan details
   * @returns PlanDto Successful Response
   * @throws ApiError
   */
  public getPlanApiV1BillingPlansPlanIdGet({
    planId,
  }: {
    planId: string,
  }): CancelablePromise<PlanDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/billing/plans/{plan_id}',
      path: {
        'plan_id': planId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete existing plan
   * @returns any Successful Response
   * @throws ApiError
   */
  public deletePlanApiV1BillingPlansPlanIdDelete({
    planId,
  }: {
    planId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/billing/plans/{plan_id}',
      path: {
        'plan_id': planId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Create a new plan
   * @returns any Successful Response
   * @throws ApiError
   */
  public createPlanApiV1BillingPlansCreatePost({
    requestBody,
  }: {
    requestBody: CreatePlanDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/billing/plans/create',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update a existing plan
   * @returns void
   * @throws ApiError
   */
  public updatePlanApiV1BillingPlansPlanIdUpdatePatch({
    planId,
    requestBody,
  }: {
    planId: string,
    requestBody: UpdatePlanDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PATCH',
      url: '/api/v1/billing/plans/{plan_id}/update',
      path: {
        'plan_id': planId,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * List invoices
   * @returns InvoiceListDto Successful Response
   * @throws ApiError
   */
  public listInvoicesApiV1BillingInvoicesGet(): CancelablePromise<InvoiceListDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/billing/invoices',
    });
  }
}
