import { useAppConfig } from "@/components/providers/app-config-provider";
import { useAuthContext } from "@/components/providers/auth-provider";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Label } from "@/components/ui/label";
import {
    Form,
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormMessage,
    FormDescription
} from "@/components/ui/form";
import { toast } from "sonner";
import { getApiClient } from "@/lib/utils";
import { UpdateTenantDto } from "@/api";
import { Building2, Globe, CheckCircle, Clock, XCircle, Plus, AlertTriangle } from "lucide-react";

const tenantFormSchema = z.object({
    custom_domain: z.string().optional().refine((val) => {
        if (!val || val.trim() === "") return true;
        // Basic domain validation regex
        const domainRegex = /^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$/;
        return domainRegex.test(val);
    }, {
        message: "Please enter a valid domain name (e.g., yourdomain.com)"
    })
});

type TenantFormData = z.infer<typeof tenantFormSchema>;

export function TenantSetting() {
    const { can } = useAuthContext();
    const { current_tenant } = useAppConfig();
    const [isLoading, setIsLoading] = useState(false);
    const [showCustomDomainForm, setShowCustomDomainForm] = useState(false);

    const hasManageTenantSetting = can("full:access") || can("manage:storage_settings");

    const form = useForm<TenantFormData>({
        resolver: zodResolver(tenantFormSchema),
        defaultValues: {
            custom_domain: current_tenant?.custom_domain || ""
        }
    });

    const getCustomDomainStatusBadge = (status: string | null) => {
        switch (status) {
            case "active":
                return <Badge variant="default" className="bg-green-100 text-green-800 border-green-200"><CheckCircle className="w-3 h-3 mr-1" />Active</Badge>;
            case "activation-progress":
                return <Badge variant="default" className="bg-yellow-100 text-yellow-800 border-yellow-200"><Clock className="w-3 h-3 mr-1" />In Progress</Badge>;
            case "failed":
                return <Badge variant="destructive"><XCircle className="w-3 h-3 mr-1" />Failed</Badge>;
            default:
                return <Badge variant="secondary">Not Set</Badge>;
        }
    };

    const onSubmit = async (data: TenantFormData) => {
        if (!current_tenant?.id) {
            toast.error("Tenant information is not available");
            return;
        }

        setIsLoading(true);
        try {
            const apiClient = getApiClient();
            const updateData: UpdateTenantDto = {
                custom_domain: data.custom_domain?.trim() || null,
                is_active: current_tenant.is_active
            };

            const response = await apiClient.tenants.updateTenantDnsRecordApiV1TenantsUpdateDnsTenantIdPost({
                tenantId: current_tenant.id,
                requestBody: updateData
            });

            toast.success(response.message || "Custom domain update requested successfully");
            setShowCustomDomainForm(false);
            // Optionally refresh the page or update the app config
            // window.location.reload();
        } catch (error: any) {
            console.error("Error updating tenant DNS:", error);
            toast.error(error?.body?.detail || "Failed to update custom domain");
        } finally {
            setIsLoading(false);
        }
    };

    if (!hasManageTenantSetting) {
        return (
            <div className="grid place-items-center place-content-center h-40">
                <p>
                    You do not have permission to view this page.
                </p>
            </div>
        );
    }

    if (!current_tenant) {
        return (
            <div className="px-4 py-6 w-full xl:container xl:mx-auto xl:w-5xl">
                <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                        Tenant information is not available. Please contact support.
                    </AlertDescription>
                </Alert>
            </div>
        );
    }

    return (
        <div className="px-4 py-6 w-full xl:container xl:mx-auto xl:w-5xl">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 space-y-4 sm:space-y-0">
                <div>
                    <h1 className="text-2xl sm:text-3xl font-bold">Tenant Settings</h1>
                    <p className="text-muted-foreground">Manage your tenant information here.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Tenant Information Card */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Building2 className="w-5 h-5" />
                            <span>Tenant Information</span>
                        </CardTitle>
                        <CardDescription>
                            Basic tenant details and status
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Tenant Name</Label>
                            <div className="font-medium">{current_tenant.name}</div>
                        </div>

                        <div className="space-y-2">
                            <Label>Subdomain</Label>
                            <div className="font-medium text-muted-foreground">
                                {current_tenant.subdomain || "Not configured"}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Status</Label>
                            <div>
                                {current_tenant.is_active ? (
                                    <Badge variant="default" className="bg-green-100 text-green-800 border-green-200">
                                        <CheckCircle className="w-3 h-3 mr-1" />
                                        Active
                                    </Badge>
                                ) : (
                                    <Badge variant="secondary">
                                        <XCircle className="w-3 h-3 mr-1" />
                                        Inactive
                                    </Badge>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Custom Domain Card */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <Globe className="w-5 h-5" />
                            <span>Custom Domain</span>
                        </CardTitle>
                        <CardDescription>
                            Configure your custom domain settings
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Current Domain</Label>
                            <div className="font-medium">
                                {current_tenant.custom_domain || (
                                    <span className="text-muted-foreground">No custom domain configured</span>
                                )}
                            </div>
                        </div>

                        <div className="space-y-2">
                            <Label>Domain Status</Label>
                            <div>
                                {getCustomDomainStatusBadge(current_tenant.custom_domain_status)}
                            </div>
                        </div>

                        {/* Add Custom Domain Button or Form */}
                        {!current_tenant.custom_domain && !showCustomDomainForm && (
                            <Button
                                onClick={() => setShowCustomDomainForm(true)}
                                className="w-full"
                                variant="outline"
                            >
                                <Plus className="w-4 h-4 mr-2" />
                                Add Custom Domain
                            </Button>
                        )}

                        {(showCustomDomainForm || current_tenant.custom_domain) && (
                            <Form {...form}>
                                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                                    <FormField
                                        control={form.control}
                                        name="custom_domain"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Custom Domain</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        placeholder="app.yourdomain.com"
                                                        disabled={isLoading}
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormDescription>
                                                    Enter your custom domain without protocol (e.g., app.yourdomain.com)
                                                </FormDescription>
                                                <FormMessage />
                                            </FormItem>
                                        )}
                                    />

                                    <div className="flex space-x-2">
                                        <Button
                                            type="submit"
                                            disabled={isLoading}
                                            className="flex-1"
                                        >
                                            {isLoading ? "Processing..." : current_tenant.custom_domain ? "Update Domain" : "Add Domain"}
                                        </Button>
                                        {showCustomDomainForm && !current_tenant.custom_domain && (
                                            <Button
                                                type="button"
                                                variant="outline"
                                                onClick={() => setShowCustomDomainForm(false)}
                                                disabled={isLoading}
                                            >
                                                Cancel
                                            </Button>
                                        )}
                                    </div>
                                </form>
                            </Form>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* DNS Configuration Instructions */}
            {(showCustomDomainForm || current_tenant.custom_domain) && (
                <Card className="mt-6">
                    <CardHeader>
                        <CardTitle className="flex items-center space-x-2">
                            <AlertTriangle className="w-5 h-5 text-amber-500" />
                            <span>DNS Configuration Required</span>
                        </CardTitle>
                        <CardDescription>
                            Follow these instructions to configure your DNS records
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <Alert>
                            <AlertDescription className="text-sm leading-relaxed">
                                <strong>Important:</strong> When bringing your own domain you must map the DNS records for your custom domain to point to our main domain.
                                You can do this by adding a CNAME record in your domain's DNS settings.
                                <br /><br />
                                <strong>Here is an example of how to set it up:</strong>
                                <br />
                                <code className="bg-muted px-2 py-1 rounded text-sm">
                                    Type: CNAME<br />
                                    Name: app<br />
                                    Value: {current_tenant.subdomain}
                                </code>
                                <br /><br />
                                After updating your DNS settings, it may take up to 24 hours for the changes to propagate.
                                You will receive an email notification once the domain is successfully configured.
                            </AlertDescription>
                        </Alert>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}