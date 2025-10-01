/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AIAskRequestDto } from '../models/AIAskRequestDto';
import type { AIHistoriesDto } from '../models/AIHistoriesDto';
import type { AIModelInfoDto } from '../models/AIModelInfoDto';
import type { AISessionByUserIdDto } from '../models/AISessionByUserIdDto';
import type { NewSessionResponseDto } from '../models/NewSessionResponseDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AiService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Models
   * @returns AIModelInfoDto Successful Response
   * @throws ApiError
   */
  public getModelsApiV1AiModelsGet(): CancelablePromise<Array<AIModelInfoDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/models',
    });
  }
  /**
   * Get History
   * @returns AISessionByUserIdDto Successful Response
   * @throws ApiError
   */
  public getHistoryApiV1AiHistoryGet(): CancelablePromise<Array<AISessionByUserIdDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/history',
    });
  }
  /**
   * Create New Session
   * @returns NewSessionResponseDto Successful Response
   * @throws ApiError
   */
  public createNewSessionApiV1AiNewSessionGet(): CancelablePromise<NewSessionResponseDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/new_session',
    });
  }
  /**
   * Get Single Session
   * @returns AIHistoriesDto Successful Response
   * @throws ApiError
   */
  public getSingleSessionApiV1AiSessionsSessionIdGet({
    sessionId,
  }: {
    sessionId: string,
  }): CancelablePromise<Array<AIHistoriesDto>> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/ai/sessions/{session_id}',
      path: {
        'session_id': sessionId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Delete Session
   * @returns any Successful Response
   * @throws ApiError
   */
  public deleteSessionApiV1AiSessionsSessionIdDelete({
    sessionId,
  }: {
    sessionId: string,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'DELETE',
      url: '/api/v1/ai/sessions/{session_id}',
      path: {
        'session_id': sessionId,
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
    requestBody: AIAskRequestDto,
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
