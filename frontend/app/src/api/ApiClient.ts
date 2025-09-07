/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import { AiService } from './services/AiService';
import { AuthService } from './services/AuthService';
import { DashboardService } from './services/DashboardService';
import { PermissionsService } from './services/PermissionsService';
import { RolesService } from './services/RolesService';
import { TenantsService } from './services/TenantsService';
import { UsersService } from './services/UsersService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class ApiClient {
  public readonly ai: AiService;
  public readonly auth: AuthService;
  public readonly dashboard: DashboardService;
  public readonly permissions: PermissionsService;
  public readonly roles: RolesService;
  public readonly tenants: TenantsService;
  public readonly users: UsersService;
  public readonly request: BaseHttpRequest;
  constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
    this.request = new HttpRequest({
      BASE: config?.BASE ?? '',
      VERSION: config?.VERSION ?? '1.0.0',
      WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
      CREDENTIALS: config?.CREDENTIALS ?? 'include',
      TOKEN: config?.TOKEN,
      USERNAME: config?.USERNAME,
      PASSWORD: config?.PASSWORD,
      HEADERS: config?.HEADERS,
      ENCODE_PATH: config?.ENCODE_PATH,
    });
    this.ai = new AiService(this.request);
    this.auth = new AuthService(this.request);
    this.dashboard = new DashboardService(this.request);
    this.permissions = new PermissionsService(this.request);
    this.roles = new RolesService(this.request);
    this.tenants = new TenantsService(this.request);
    this.users = new UsersService(this.request);
  }
}

