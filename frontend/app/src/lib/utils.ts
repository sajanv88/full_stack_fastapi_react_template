import { ApiClient, type TenantDto } from "@/api"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function setTenant(tenant: TenantDto | null) {
  if (!tenant) {
    localStorage.removeItem("_tenant");
    window.dispatchEvent(new Event("tenant_removed"));

    return;
  }
  localStorage.setItem("_tenant", JSON.stringify(tenant));
  window.dispatchEvent(new Event("tenant_set"));

}

export function getTenant(): TenantDto | null {
  const tenant = localStorage.getItem("_tenant");
  return tenant ? JSON.parse(tenant) : null;
}


export function formatPrice(amount: number, currency: string) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency.toUpperCase(),
  }).format(amount / 100);
};

export function formatDate(timestamp: number) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(timestamp * 1000));
};

export function formatDateWithHourAndMinute(timestamp: number | null | undefined) {
  if (timestamp == null) return "N/A";
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(timestamp * 1000));
};

export function getApiClient(accessToken?: string) {
  // console.log("Getting API client with access token:", accessToken);
  const tenant = getTenant();
  if (!accessToken) {
    if (tenant) {
      return new ApiClient({
        HEADERS: {
          "X-Tenant-ID": tenant.id!
        },
        WITH_CREDENTIALS: true,
      })
    }
    return new ApiClient({
      WITH_CREDENTIALS: true,
    });
  }
  return new ApiClient({
    HEADERS: {
      Authorization: `Bearer ${accessToken}`,
      ...tenant?.id && { "X-Tenant-ID": tenant.id }
    },
    WITH_CREDENTIALS: true
  });
}


export function extractErrorMessage(error: unknown): string {
  const err = JSON.stringify(error);
  return error instanceof Error ? JSON.parse(err).body.error : "Something went wrong.";
}