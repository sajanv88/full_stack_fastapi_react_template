/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AiModel } from '../models/AiModel';
import type { AIRequest } from '../models/AIRequest';
import type { AIResponse } from '../models/AIResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AiService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Models
   * @returns AiModel Successful Response
   * @throws ApiError
   */
  public getModelsApiV1AiModelsGet(): CancelablePromise<Array<AiModel>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/models',
    });
  }
  /**
   * Get History
   * @returns AIResponse Successful Response
   * @throws ApiError
   */
  public getHistoryApiV1AiHistoryGet(): CancelablePromise<Array<AIResponse>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/history',
    });
  }
  /**
   * Get History Item
   * @returns AIResponse Successful Response
   * @throws ApiError
   */
  public getHistoryItemApiV1AiHistoryHistoryIdGet({
    historyId,
  }: {
    historyId: string,
  }): CancelablePromise<AIResponse> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/history/{history_id}',
      path: {
        'history_id': historyId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Set Preferred Model
   * @returns void
   * @throws ApiError
   */
  public setPreferredModelApiV1AiSetModelPreferenceModelNamePut({
    modelName,
  }: {
    modelName: string,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/ai/set_model_preference/{model_name}',
      path: {
        'model_name': modelName,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Ask Ai
   * @returns any Successful Response
   * @throws ApiError
   */
  public askAiApiV1AiAskPost({
    requestBody,
  }: {
    requestBody: AIRequest,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/ai/ask',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
