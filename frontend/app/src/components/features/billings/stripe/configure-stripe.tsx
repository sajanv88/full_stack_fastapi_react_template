import { useStripeProvider } from "@/components/providers/stripe-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
    CreditCard,
    Key,
    Webhook,
    DollarSign,
    Calendar,
    Settings,
    CheckCircle2,
    AlertTriangle,
    Eye,
    EyeOff,
    RefreshCw
} from "lucide-react";
import { IconExternalLink } from "@tabler/icons-react";
import { useState } from "react";
import { useAppConfig } from "@/components/providers/app-config-provider";

const stripeConfigSchema = z.object({
    stripe_secret_key: z.string().min(1, "Stripe secret key is required"),
    stripe_webhook_secret: z.string().min(1, "Webhook secret is required"),
    default_currency: z.string().min(3, "Currency code is required").max(3, "Currency code must be 3 characters"),
    mode: z.enum(["one_time", "recurring", "both"]),
    trial_period_days: z.number().min(0, "Trial period must be 0 or more").max(365, "Trial period cannot exceed 365 days"),
});

type StripeConfigForm = z.infer<typeof stripeConfigSchema>;

export function ConfigureStripe() {
    const { current_tenant } = useAppConfig();
    const { loading, showConfigureStripe, onConfigureStripe, configuredStripeSetting, onRefreshStripeSetting } = useStripeProvider();
    const [showSecretKey, setShowSecretKey] = useState(false);
    const [showWebhookSecret, setShowWebhookSecret] = useState(false);

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        formState: { errors, isSubmitting },
    } = useForm<StripeConfigForm>({
        resolver: zodResolver(stripeConfigSchema),
        defaultValues: {
            default_currency: configuredStripeSetting?.default_currency || "EUR",
            mode: configuredStripeSetting?.mode || "both",
            trial_period_days: configuredStripeSetting?.trial_period_days || 0,
            stripe_secret_key: "",
            stripe_webhook_secret: "",
        },
    });

    const selectedMode = watch("mode");

    const onSubmit = async (data: StripeConfigForm) => {
        await onConfigureStripe({
            stripe_secret_key: data.stripe_secret_key,
            stripe_webhook_secret: data.stripe_webhook_secret,
            default_currency: data.default_currency.toLowerCase(),
            mode: data.mode,
            trial_period_days: data.trial_period_days,
        });
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="flex flex-col items-center gap-4">
                    <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">Loading Stripe configuration...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 xl:container xl:mx-auto xl:max-w-4xl">
            {/* Header Section */}
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <CreditCard className="h-6 w-6" />
                        Stripe Configuration
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        Configure your Stripe payment gateway settings for your <strong className="capitalize">{current_tenant?.name}'s</strong> users
                    </p>
                </div>
                {configuredStripeSetting && (
                    <Badge variant="default" className="flex items-center gap-1">
                        <CheckCircle2 className="h-3 w-3" />
                        Configured
                    </Badge>
                )}
            </div>

            {/* Current Configuration Display */}
            {configuredStripeSetting && !showConfigureStripe && (
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2">
                                    <Settings className="h-5 w-5" />
                                    Current Configuration
                                </CardTitle>
                                <CardDescription>Your active Stripe settings</CardDescription>
                            </div>
                            <Button onClick={onRefreshStripeSetting} variant="outline" size="sm">
                                <RefreshCw className="h-4 w-4 mr-2" />
                                Refresh
                            </Button>
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                                <DollarSign className="h-5 w-5 text-muted-foreground mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium">Default Currency</p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {configuredStripeSetting.default_currency.toUpperCase()}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                                <CreditCard className="h-5 w-5 text-muted-foreground mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium">Payment Mode</p>
                                    <p className="text-xs text-muted-foreground mt-1 capitalize">
                                        {configuredStripeSetting.mode.replace('_', ' ')}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium">Trial Period</p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {configuredStripeSetting.trial_period_days} days
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                                <Settings className="h-5 w-5 text-muted-foreground mt-0.5" />
                                <div>
                                    <p className="text-sm font-medium">Tenant ID</p>
                                    <p className="text-xs text-muted-foreground mt-1 font-mono">
                                        {configuredStripeSetting.tenant_id}
                                    </p>
                                </div>
                            </div>
                        </div>

                        <Separator />

                        <Alert>
                            <AlertTriangle className="h-4 w-4" />
                            <AlertDescription>
                                To update your configuration, please contact support or use the configuration form below.
                            </AlertDescription>
                        </Alert>
                    </CardContent>
                </Card>
            )}

            {/* Configuration Form */}
            {(showConfigureStripe || !configuredStripeSetting) && (
                <form onSubmit={handleSubmit(onSubmit)}>
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Key className="h-5 w-5" />
                                {configuredStripeSetting ? "Update" : "Configure"} Stripe Settings
                            </CardTitle>
                            <CardDescription>
                                Enter your Stripe API credentials and payment configuration
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* API Credentials Section */}
                            <div className="space-y-4">
                                <div className="flex items-center gap-2">
                                    <Key className="h-4 w-4 text-muted-foreground" />
                                    <h3 className="font-semibold">API Credentials</h3>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="stripe_secret_key">
                                        Stripe Secret Key <span className="text-destructive">*</span>
                                    </Label>
                                    <div className="relative">
                                        <Input
                                            id="stripe_secret_key"
                                            type={showSecretKey ? "text" : "password"}
                                            placeholder="sk_test_... or sk_live_..."
                                            {...register("stripe_secret_key")}
                                            className="pr-10"
                                        />
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="sm"
                                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                                            onClick={() => setShowSecretKey(!showSecretKey)}
                                        >
                                            {showSecretKey ? (
                                                <EyeOff className="h-4 w-4" />
                                            ) : (
                                                <Eye className="h-4 w-4" />
                                            )}
                                        </Button>
                                    </div>
                                    {errors.stripe_secret_key && (
                                        <p className="text-sm text-destructive">{errors.stripe_secret_key.message}</p>
                                    )}
                                    <p className="text-xs text-muted-foreground">
                                        Get this from your Stripe Dashboard → Developers → API keys
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="stripe_webhook_secret">
                                        Webhook Secret <span className="text-destructive">*</span>
                                    </Label>
                                    <div className="relative">
                                        <Input
                                            id="stripe_webhook_secret"
                                            type={showWebhookSecret ? "text" : "password"}
                                            placeholder="whsec_..."
                                            {...register("stripe_webhook_secret")}
                                            className="pr-10"
                                        />
                                        <Button
                                            type="button"
                                            variant="ghost"
                                            size="sm"
                                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                                            onClick={() => setShowWebhookSecret(!showWebhookSecret)}
                                        >
                                            {showWebhookSecret ? (
                                                <EyeOff className="h-4 w-4" />
                                            ) : (
                                                <Eye className="h-4 w-4" />
                                            )}
                                        </Button>
                                    </div>
                                    {errors.stripe_webhook_secret && (
                                        <p className="text-sm text-destructive">{errors.stripe_webhook_secret.message}</p>
                                    )}
                                    <p className="text-xs text-muted-foreground">
                                        Get this from Stripe Dashboard → Developers → Webhooks
                                    </p>
                                </div>
                            </div>

                            <Separator />

                            {/* Payment Configuration Section */}
                            <div className="space-y-4">
                                <div className="flex items-center gap-2">
                                    <CreditCard className="h-4 w-4 text-muted-foreground" />
                                    <h3 className="font-semibold">Payment Configuration</h3>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label htmlFor="default_currency">
                                            Default Currency <span className="text-destructive">*</span>
                                        </Label>
                                        <Input
                                            id="default_currency"
                                            placeholder="USD"
                                            maxLength={3}
                                            {...register("default_currency")}
                                            className="uppercase"
                                        />
                                        {errors.default_currency && (
                                            <p className="text-sm text-destructive">{errors.default_currency.message}</p>
                                        )}
                                        <p className="text-xs text-muted-foreground">
                                            3-letter ISO currency code (e.g., USD, EUR, GBP)
                                        </p>
                                    </div>

                                    <div className="space-y-2">
                                        <Label htmlFor="trial_period_days">
                                            Trial Period (Days)
                                        </Label>
                                        <Input
                                            id="trial_period_days"
                                            type="number"
                                            min="0"
                                            max="365"
                                            placeholder="0"
                                            {...register("trial_period_days")}
                                        />
                                        {errors.trial_period_days && (
                                            <p className="text-sm text-destructive">{errors.trial_period_days.message}</p>
                                        )}
                                        <p className="text-xs text-muted-foreground">
                                            Number of free trial days (0 for no trial)
                                        </p>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="mode">
                                        Payment Mode <span className="text-destructive">*</span>
                                    </Label>
                                    <Select
                                        value={selectedMode}
                                        onValueChange={(value) => setValue("mode", value as "one_time" | "recurring" | "both")}
                                    >
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select payment mode" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="one_time">
                                                <div className="flex items-center gap-2">
                                                    <DollarSign className="h-4 w-4" />
                                                    <span>One-time Payment</span>
                                                </div>
                                            </SelectItem>
                                            <SelectItem value="recurring">
                                                <div className="flex items-center gap-2">
                                                    <RefreshCw className="h-4 w-4" />
                                                    <span>Recurring Subscription</span>
                                                </div>
                                            </SelectItem>
                                            <SelectItem value="both">
                                                <div className="flex items-center gap-2">
                                                    <CreditCard className="h-4 w-4" />
                                                    <span>Both (One-time & Recurring)</span>
                                                </div>
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>
                                    {errors.mode && (
                                        <p className="text-sm text-destructive">{errors.mode.message}</p>
                                    )}
                                    <p className="text-xs text-muted-foreground">
                                        Choose which payment types you want to accept
                                    </p>
                                </div>
                            </div>

                            <Separator />

                            {/* Security Notice */}
                            <Alert>
                                <AlertTriangle className="h-4 w-4" />
                                <AlertDescription>
                                    <strong>Security Notice:</strong> Your API keys are encrypted and stored securely.
                                    Never share your secret keys or commit them to version control.
                                </AlertDescription>
                            </Alert>

                            {/* Action Buttons */}
                            <div className="flex flex-col sm:flex-row gap-3 pt-4">
                                <Button
                                    type="submit"
                                    className="flex-1"
                                    disabled={isSubmitting}
                                >
                                    {isSubmitting ? (
                                        <>
                                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                            Configuring...
                                        </>
                                    ) : (
                                        <>
                                            <CheckCircle2 className="w-4 h-4 mr-2" />
                                            {configuredStripeSetting ? "Update" : "Configure"} Stripe
                                        </>
                                    )}
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </form>
            )}

            {/* Help Section */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Need Help?</CardTitle>
                    <CardDescription>Resources to help you get started with Stripe</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                            <Key className="h-5 w-5 text-muted-foreground mt-0.5" />
                            <div>
                                <p className="text-sm font-medium">API Keys</p>
                                <a
                                    href="https://dashboard.stripe.com/apikeys"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-primary hover:underline"
                                >
                                    Get your API keys <IconExternalLink className="w-3 inline" />
                                </a>
                            </div>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                            <Webhook className="h-5 w-5 text-muted-foreground mt-0.5" />
                            <div>
                                <p className="text-sm font-medium">Webhooks</p>
                                <a
                                    href="https://dashboard.stripe.com/webhooks"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-primary hover:underline"
                                >
                                    Configure webhooks <IconExternalLink className="w-3 inline" />
                                </a>
                            </div>
                        </div>
                        <div className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                            <Settings className="h-5 w-5 text-muted-foreground mt-0.5" />
                            <div>
                                <p className="text-sm font-medium">Documentation</p>
                                <a
                                    href="https://stripe.com/docs"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-xs text-primary hover:underline"
                                >
                                    Read the docs <IconExternalLink className="w-3 inline" />
                                </a>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}