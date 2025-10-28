import { useEffect, useState } from "react";
import { useStripeProvider } from "@/components/providers/stripe-provider";
import { useAuthContext } from "@/components/providers/auth-provider";
import { formatPrice, getApiClient } from "@/lib/utils";
import { PlanDto } from "@/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import {
    CreditCard,
    Calendar,
    TrendingUp,
    Package,
    RefreshCw,
    CheckCircle2,
    XCircle,
    Zap,
} from "lucide-react";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { ShowScreenLoader } from "@/components/shared/show-screen-loader";
import { ConfigureStripeNow } from "@/components/features/billings/stripe/configure-stripe-now";
import { AddANewPlan } from "./add-a-new-plan";

export function BillingOverview() {
    const { configuredStripeSetting, loading: stripeLoading, stripeConfigurationError } = useStripeProvider();
    const { current_tenant } = useAppConfig();
    const { accessToken } = useAuthContext();
    const [plans, setPlans] = useState<PlanDto[]>([]);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(false);
    const [planError, setPlanError] = useState<string | null>(null);

    const fetchPlans = async () => {
        if (!accessToken) return;
        try {
            setLoading(true);
            const response = await getApiClient(accessToken).stripeBilling.listPlansApiV1BillingPlansGet();
            setPlans(response.plans);
            setHasMore(response.has_more);
            setPlanError(null);
        } catch (error) {
            console.error("Error fetching plans:", error);
            setPlanError("Failed to load plans. Please try again later.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (accessToken && current_tenant && configuredStripeSetting) {
            fetchPlans();
        } else if (!current_tenant) {
            // This is to handle cases where there is no tenant (Host Mode)
            fetchPlans();
        }
    }, [accessToken, current_tenant, configuredStripeSetting]);



    const formatInterval = (interval: string, count: number) => {
        const unit = count > 1 ? `${count} ${interval}s` : interval;
        return `per ${unit}`;
    };

    if ((stripeLoading || loading) && !stripeConfigurationError) {
        return <ShowScreenLoader message="Loading billing information..." />
    }

    if (plans.length === 0 && !planError && !stripeConfigurationError) {
        return (
            <Alert>
                <CreditCard className="h-4 w-4" />
                <AlertDescription>
                    No plans available. Please create a billing plan to get started.
                </AlertDescription>
            </Alert>
        );
    }

    if (planError) {
        return (
            <Alert variant="destructive">
                <CreditCard className="h-4 w-4" />
                <AlertDescription>
                    {planError}
                </AlertDescription>
            </Alert>
        );
    }

    // This check is to prompt user to configure Stripe if there is a configuration error for the tenant
    if (stripeConfigurationError && current_tenant) {
        return <ConfigureStripeNow />
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <TrendingUp className="h-6 w-6" />
                        Billing Overview
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        View and manage your billing plans and subscription details
                    </p>
                </div>
                <div className="flex items-center space-x-2">
                    <Button onClick={fetchPlans} variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                    <AddANewPlan onPlanCreated={fetchPlans} />
                </div>
            </div>



            {/* Available Plans */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2">
                                <Zap className="h-5 w-5" />
                                Available Plans
                            </CardTitle>
                            <CardDescription>
                                {plans.length} {plans.length === 1 ? "plan" : "plans"} configured
                                {hasMore && " (showing partial results)"}
                            </CardDescription>

                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {plans.length === 0 ? (
                        <div className="text-center py-12">
                            <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                            <h3 className="text-lg font-semibold mb-2">No Plans Available</h3>
                            <p className="text-muted-foreground text-sm">
                                Create your first billing plan to get started
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {plans.map((plan) => (
                                <Card key={plan.id} className="relative">
                                    <CardHeader className="pb-3">
                                        <div className="flex items-start justify-between">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <Badge
                                                        variant={plan.active ? "default" : "secondary"}
                                                        className="flex items-center gap-1"
                                                    >
                                                        {plan.active ? (
                                                            <>
                                                                <CheckCircle2 className="h-3 w-3" />
                                                                Active
                                                            </>
                                                        ) : (
                                                            <>
                                                                <XCircle className="h-3 w-3" />
                                                                Inactive
                                                            </>
                                                        )}
                                                    </Badge>
                                                </div>
                                                <CardTitle className="text-xl">
                                                    {formatPrice(plan.amount, plan.currency || 'EUR')}
                                                </CardTitle>
                                                <CardDescription className="text-xs mt-1">
                                                    {formatInterval(plan.interval, plan.interval_count)}
                                                </CardDescription>
                                            </div>
                                        </div>
                                    </CardHeader>
                                    <CardContent className="space-y-3 pt-0">
                                        <Separator />
                                        <div className="space-y-2 text-sm">
                                            <div className="flex items-center justify-between">
                                                <span className="text-muted-foreground">Billing Scheme</span>
                                                <span className="font-medium capitalize">{plan.billing_scheme}</span>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <span className="text-muted-foreground">Usage Type</span>
                                                <span className="font-medium capitalize">{plan.usage_type}</span>
                                            </div>
                                            {plan.trial_period_days != null && plan.trial_period_days > 0 && (
                                                <div className="flex items-center justify-between">
                                                    <span className="text-muted-foreground">Trial Period</span>
                                                    <span className="font-medium">{plan.trial_period_days} days</span>
                                                </div>
                                            )}
                                        </div>
                                        <Separator />
                                        <div className="space-y-1">
                                            <p className="text-xs text-muted-foreground">Plan ID</p>
                                            <p className="text-xs font-mono bg-muted p-2 rounded truncate">
                                                {plan.id}
                                            </p>
                                        </div>
                                        <div className="space-y-1">
                                            <p className="text-xs text-muted-foreground">Product ID</p>
                                            <p className="text-xs font-mono bg-muted p-2 rounded truncate">
                                                {plan.product}
                                            </p>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Total Plans</p>
                                <p className="text-2xl font-bold mt-1">{plans.length}</p>
                            </div>
                            <Package className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Active Plans</p>
                                <p className="text-2xl font-bold mt-1 text-green-600">
                                    {plans.filter((p) => p.active).length}
                                </p>
                            </div>
                            <CheckCircle2 className="h-8 w-8 text-green-600" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Inactive Plans</p>
                                <p className="text-2xl font-bold mt-1 text-muted-foreground">
                                    {plans.filter((p) => !p.active).length}
                                </p>
                            </div>
                            <XCircle className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground">Recurring Plans</p>
                                <p className="text-2xl font-bold mt-1">
                                    {plans.filter((p) => p.interval !== "one_time").length}
                                </p>
                            </div>
                            <Calendar className="h-8 w-8 text-muted-foreground" />
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
