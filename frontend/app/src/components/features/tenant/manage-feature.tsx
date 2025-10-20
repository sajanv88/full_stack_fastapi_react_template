import { FeatureDto, Feature } from "@/api";
import { useAuthContext } from "@/components/providers/auth-provider";
import { useTenants } from "@/components/providers/tenant-provider";
import { Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { cn, getApiClient } from "@/lib/utils";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import {
    MessageSquare,
    FileBarChart,
    TrendingUp,
    Building2,
    Users,
    Loader2,
    CheckCircle,
    XCircle
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ManageFeatureTenantDialogProps {
    open: boolean;
    onDismiss: () => void;
}
export function ManageFeature({ open, onDismiss }: ManageFeatureTenantDialogProps) {
    const { selectedTenant, refreshTenants } = useTenants();
    const { accessToken } = useAuthContext();
    const [features, setFeatures] = useState<Array<FeatureDto>>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [updatingFeature, setUpdatingFeature] = useState<string | null>(null);

    async function fetchFeatures() {
        setIsLoading(true);
        try {
            const apiClient = getApiClient(accessToken);
            const tenantFeatures = await apiClient.tenants.getTenantFeaturesApiV1TenantsTenantIdFeaturesGet({
                tenantId: selectedTenant!.tenant.id!
            });
            setFeatures(tenantFeatures);
        } catch (error) {
            console.error("Error fetching features:", error);
            toast.error("Failed to load features");
        } finally {
            setIsLoading(false);
        }
    }


    async function updateFeature(featureName: Feature, enabled: boolean) {
        setUpdatingFeature(featureName);
        try {
            const apiClient = getApiClient(accessToken);
            await apiClient.tenants.updateTenantFeatureApiV1TenantsTenantIdUpdateFeaturePatch({
                tenantId: selectedTenant!.tenant.id!,
                requestBody: {
                    name: featureName,
                    enabled: enabled
                }
            });
            toast.success(`Feature '${featureName}' ${enabled ? 'enabled' : 'disabled'} successfully.`, {
                richColors: true,
                position: "top-right"
            });
            setFeatures((prevFeatures) =>
                prevFeatures.map((feature) =>
                    feature.name === featureName ? { ...feature, enabled } : feature
                )
            );
        } catch (error) {
            console.error("Error updating feature:", error);
            toast.error(`Failed to update feature '${featureName}'.`, {
                richColors: true,
                position: "top-right"
            });
        } finally {
            setUpdatingFeature(null);
        }
    }

    const getFeatureIcon = (featureName: string) => {
        switch (featureName.toLowerCase()) {
            case 'chat':
            case 'messaging':
                return <MessageSquare className="w-5 h-5" />;
            case 'analytics':
            case 'reports':
                return <FileBarChart className="w-5 h-5" />;
            case 'dashboard':
            case 'metrics':
                return <TrendingUp className="w-5 h-5" />;
            case 'tenant':
            case 'organization':
                return <Building2 className="w-5 h-5" />;
            case 'users':
            case 'user_management':
                return <Users className="w-5 h-5" />;
            default:
                return <CheckCircle className="w-5 h-5" />;
        }
    };

    const getFeatureDescription = (featureName: string) => {
        switch (featureName.toLowerCase()) {
            case 'chat':
                return 'Enable chat functionality for tenant users';
            case 'messaging':
                return 'Allow internal messaging between users';
            case 'analytics':
                return 'Access to advanced analytics and insights';
            case 'reports':
                return 'Generate and export detailed reports';
            case 'dashboard':
                return 'Access to the main dashboard interface';
            case 'metrics':
                return 'View performance metrics and KPIs';
            case 'tenant':
                return 'Tenant management and configuration';
            case 'organization':
                return 'Organization-level settings and controls';
            case 'users':
                return 'User management and administration';
            case 'user_management':
                return 'Advanced user management capabilities';
            default:
                return `Manage ${featureName} functionality`;
        }
    };

    function onCloseDialog(flag: boolean) {
        if (!flag) {
            refreshTenants();
            onDismiss();
        }
    }

    useEffect(() => {
        if (!open) return;
        fetchFeatures();
    }, [open, accessToken, selectedTenant?.tenant.id]);

    return (
        <Dialog open={open} onOpenChange={onCloseDialog}>
            <DialogContent className="w-full md:max-w-screen-md">
                <DialogTitle>
                    Manage Features for Tenant: {selectedTenant?.tenant.name}
                </DialogTitle>
                <DialogDescription>
                    You can manage the features for this tenant here.
                </DialogDescription>
                <section className="mt-4">
                    {isLoading ? (
                        <div className="flex items-center justify-center py-8">
                            <Loader2 className="w-6 h-6 animate-spin mr-2" />
                            <span>Loading features...</span>
                        </div>
                    ) : features.length === 0 ? (
                        <div className="text-center py-8">
                            <XCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                            <p className="text-muted-foreground">No features available for this tenant.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold">Feature Management</h3>
                                <Badge variant="outline">
                                    {features.filter(f => f.enabled).length} of {features.length} enabled
                                </Badge>
                            </div>

                            <Separator />
                            <ScrollArea className="h-[400px]">
                                <div className="grid gap-2 sm:grid-cols-2 sm:mr-3">
                                    {features.map((feature) => (
                                        <Card key={feature.name} className="transition-all hover:shadow-md">
                                            <CardContent className="p-0 px-2">
                                                <div className="flex  justify-between items-start">
                                                    <div className="flex items-center space-x-3">
                                                        <div className={cn("p-1 rounded-lg", feature.enabled
                                                            ? 'bg-green-100 text-green-600'
                                                            : 'bg-gray-100 text-gray-400')}>
                                                            {getFeatureIcon(feature.name)}
                                                        </div>
                                                        <div className="flex-1">
                                                            <div className="flex items-center space-x-2">
                                                                <h4 className="font-medium capitalize">
                                                                    {feature.name.replace('_', ' ')}
                                                                </h4>
                                                                <Badge
                                                                    variant={feature.enabled ? "default" : "secondary"}
                                                                    className={feature.enabled ? "bg-green-100 text-green-800" : ""}
                                                                >
                                                                    {feature.enabled ? "Enabled" : "Disabled"}
                                                                </Badge>
                                                            </div>
                                                            <p className="text-sm text-muted-foreground mt-1">
                                                                {getFeatureDescription(feature.name)}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center space-x-2">
                                                        {updatingFeature === feature.name && (
                                                            <Loader2 className="w-4 h-4 animate-spin" />
                                                        )}
                                                        <Switch
                                                            checked={feature.enabled}
                                                            onCheckedChange={(checked) =>
                                                                updateFeature(feature.name, checked)
                                                            }
                                                            disabled={updatingFeature === feature.name}
                                                        />
                                                    </div>
                                                </div>
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            </ScrollArea>

                            <div className="mt-6 p-4 bg-muted/50 rounded-lg">
                                <p className="text-sm text-muted-foreground">
                                    <strong>Note:</strong> Feature changes take effect immediately.
                                    Users may need to refresh their browser to see the changes.
                                </p>
                            </div>
                        </div>
                    )}
                </section>
            </DialogContent>
        </Dialog>
    )
}