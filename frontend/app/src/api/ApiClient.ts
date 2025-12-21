/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import { AccountService } from './services/AccountService';
import { AiService } from './services/AiService';
import { AppConfigurationService } from './services/AppConfigurationService';
import { AuditLogsService } from './services/AuditLogsService';
import { BrandingService } from './services/BrandingService';
import { DashboardService } from './services/DashboardService';
import { FeaturesService } from './services/FeaturesService';
import { HealthService } from './services/HealthService';
import { ManageSecurityService } from './services/ManageSecurityService';
import { NotificationsService } from './services/NotificationsService';
import { PermissionsService } from './services/PermissionsService';
import { RolesService } from './services/RolesService';
import { SsoSettingsService } from './services/SsoSettingsService';
import { StorageSettingsService } from './services/StorageSettingsService';
import { StripeService } from './services/StripeService';
import { StripeBillingService } from './services/StripeBillingService';
import { StripeCheckoutService } from './services/StripeCheckoutService';
import { StripeInvoicesService } from './services/StripeInvoicesService';
import { StripePricingService } from './services/StripePricingService';
import { StripeProductsService } from './services/StripeProductsService';
import { TenantsService } from './services/TenantsService';
import { UsersService } from './services/UsersService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class ApiClient {
  public readonly account: AccountService;
  public readonly ai: AiService;
  public readonly appConfiguration: AppConfigurationService;
  public readonly auditLogs: AuditLogsService;
  public readonly branding: BrandingService;
  public readonly dashboard: DashboardService;
  public readonly features: FeaturesService;
  public readonly health: HealthService;
  public readonly manageSecurity: ManageSecurityService;
  public readonly notifications: NotificationsService;
  public readonly permissions: PermissionsService;
  public readonly roles: RolesService;
  public readonly ssoSettings: SsoSettingsService;
  public readonly storageSettings: StorageSettingsService;
  public readonly stripe: StripeService;
  public readonly stripeBilling: StripeBillingService;
  public readonly stripeCheckout: StripeCheckoutService;
  public readonly stripeInvoices: StripeInvoicesService;
  public readonly stripePricing: StripePricingService;
  public readonly stripeProducts: StripeProductsService;
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
    this.account = new AccountService(this.request);
    this.ai = new AiService(this.request);
    this.appConfiguration = new AppConfigurationService(this.request);
    this.auditLogs = new AuditLogsService(this.request);
    this.branding = new BrandingService(this.request);
    this.dashboard = new DashboardService(this.request);
    this.features = new FeaturesService(this.request);
    this.health = new HealthService(this.request);
    this.manageSecurity = new ManageSecurityService(this.request);
    this.notifications = new NotificationsService(this.request);
    this.permissions = new PermissionsService(this.request);
    this.roles = new RolesService(this.request);
    this.ssoSettings = new SsoSettingsService(this.request);
    this.storageSettings = new StorageSettingsService(this.request);
    this.stripe = new StripeService(this.request);
    this.stripeBilling = new StripeBillingService(this.request);
    this.stripeCheckout = new StripeCheckoutService(this.request);
    this.stripeInvoices = new StripeInvoicesService(this.request);
    this.stripePricing = new StripePricingService(this.request);
    this.stripeProducts = new StripeProductsService(this.request);
    this.tenants = new TenantsService(this.request);
    this.users = new UsersService(this.request);
  }
}

