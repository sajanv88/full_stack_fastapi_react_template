import { ApiClient, type TenantDto } from "@/api"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function setTenant(tenant: TenantDto | null) {
  if (!tenant) {
    localStorage.removeItem("_tenant");
    return;
  }
  localStorage.setItem("_tenant", JSON.stringify(tenant));
}

export function getTenant(): TenantDto | null {
  const tenant = localStorage.getItem("_tenant");
  return tenant ? JSON.parse(tenant) : null;
}



export function userProfileImageUrl(url: string | null | undefined) {
  if (!url) return "https://github.com/evilrabbit.png";
  return url;
}


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


