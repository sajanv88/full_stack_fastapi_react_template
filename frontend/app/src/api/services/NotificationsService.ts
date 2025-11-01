/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateNotificationBannerSettingDto } from '../models/CreateNotificationBannerSettingDto';
import type { NotificationBannerSettingDto } from '../models/NotificationBannerSettingDto';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class NotificationsService {
  constructor(public readonly httpRequest: BaseHttpRequest) {}
  /**
   * Get Notification Banner
   * Get the current notification banner information.
   * @returns NotificationBannerSettingDto Successful Response
   * @throws ApiError
   */
  public getNotificationBannerApiV1NotificationsBannerGet(): CancelablePromise<NotificationBannerSettingDto> {
    return this.httpRequest.request({
      method: 'GET',
      url: '/api/v1/notifications/banner',
    });
  }
  /**
   * Create Notification Banner
   * Create a new notification banner setting.
   * @returns any Successful Response
   * @throws ApiError
   */
  public createNotificationBannerApiV1NotificationsBannerPost({
    requestBody,
  }: {
    requestBody: CreateNotificationBannerSettingDto,
  }): CancelablePromise<any> {
    return this.httpRequest.request({
      method: 'POST',
      url: '/api/v1/notifications/banner',
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
  /**
   * Update Notification Banner
   * Update an existing notification banner setting.
   * @returns void
   * @throws ApiError
   */
  public updateNotificationBannerApiV1NotificationsBannerIdPut({
    id,
    requestBody,
  }: {
    id: string,
    requestBody: CreateNotificationBannerSettingDto,
  }): CancelablePromise<void> {
    return this.httpRequest.request({
      method: 'PUT',
      url: '/api/v1/notifications/banner/{id}',
      path: {
        'id': id,
      },
      body: requestBody,
      mediaType: 'application/json',
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
