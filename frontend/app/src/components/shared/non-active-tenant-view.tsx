import { useEffect } from "react";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { useNavigate } from "react-router";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
    AlertTriangle,
    Building2,
    Mail,
    Phone,
    RefreshCw,
    ArrowLeft,
    Clock,
    Shield
} from "lucide-react";
import { Logo } from "./logo";

export function NonActiveTenantView() {
    const { current_tenant, reloadAppConfig } = useAppConfig();
    const navigate = useNavigate();

    useEffect(() => {
        if (current_tenant?.is_active) {
            // Redirect to the dashboard or any other page
            navigate("/dashboard");
        }
    }, [current_tenant, navigate]);

    const handleRefresh = () => {
        reloadAppConfig();
    };

    const handleGoBack = () => {
        navigate("/");
    };

    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <div className="w-full max-w-2xl mx-auto">
                {/* Logo */}
                <div className="text-center mb-8">
                    <Logo size="lg" className="justify-center" />
                </div>

                {/* Main Card */}
                <Card className="shadow-lg border bg-card">
                    <CardHeader className="text-center pb-2">
                        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-secondary">
                            <AlertTriangle className="h-8 w-8 text-secondary-foreground" />
                        </div>
                        <CardTitle className="text-2xl font-bold text-card-foreground">
                            Account Temporarily Inactive
                        </CardTitle>
                        <CardDescription className="text-lg text-muted-foreground mt-2">
                            Your tenant account is currently inactive and requires activation
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-6">
                        {/* Tenant Information */}
                        {current_tenant && (
                            <div className="bg-muted rounded-lg p-4">
                                <div className="flex items-center gap-3 mb-3">
                                    <Building2 className="h-5 w-5 text-muted-foreground" />
                                    <h3 className="font-semibold text-foreground">Tenant Information</h3>
                                </div>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Organization:</span>
                                        <span className="font-medium capitalize">{current_tenant.name}</span>
                                    </div>
                                    {current_tenant.subdomain && (
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Subdomain:</span>
                                            <span className="font-medium">{current_tenant.subdomain}</span>
                                        </div>
                                    )}
                                    {current_tenant.custom_domain && (
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Custom Domain:</span>
                                            <span className="font-medium">{current_tenant.custom_domain}</span>
                                        </div>
                                    )}
                                    <div className="flex justify-between items-center">
                                        <span className="text-muted-foreground">Status:</span>
                                        <Badge variant="destructive">
                                            <Clock className="w-3 h-3 mr-1" />
                                            Inactive
                                        </Badge>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Status Alert */}
                        <Alert>
                            <Shield className="h-4 w-4" />
                            <AlertDescription>
                                <strong>What does this mean?</strong>
                                <p>
                                    Your account setup is complete, but your <em className="capitalize pr-1">{current_tenant?.name}</em>
                                    needs to be activated by an Host before you can access the full platform.
                                </p>
                            </AlertDescription>
                        </Alert>

                        <Separator />

                        {/* Next Steps */}
                        <div className="space-y-4">
                            <h3 className="font-semibold text-foreground flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4" />
                                Next Steps
                            </h3>
                            <div className="space-y-3 text-sm">
                                <div className="flex items-start gap-3">
                                    <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                                        1
                                    </div>
                                    <div>
                                        <p className="font-medium">Contact your host</p>
                                        <p className="text-muted-foreground">Reach out to your host to activate your account</p>
                                    </div>
                                </div>
                                <div className="flex items-start gap-3">
                                    <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                                        2
                                    </div>
                                    <div>
                                        <p className="font-medium">Wait for activation</p>
                                        <p className="text-muted-foreground">Your host will activate your tenant account</p>
                                    </div>
                                </div>
                                <div className="flex items-start gap-3">
                                    <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-semibold">
                                        3
                                    </div>
                                    <div>
                                        <p className="font-medium">Refresh this page</p>
                                        <p className="text-muted-foreground">Once activated, refresh to access your dashboard</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <Separator />

                        {/* Contact Information */}
                        <div className="space-y-4">
                            <h3 className="font-semibold text-foreground">Need Help?</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                                    <Mail className="h-4 w-4 text-muted-foreground" />
                                    <div>
                                        <p className="text-sm font-medium">Email Support</p>
                                        <p className="text-xs text-muted-foreground">support@example.com</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                                    <Phone className="h-4 w-4 text-muted-foreground" />
                                    <div>
                                        <p className="text-sm font-medium">Phone Support</p>
                                        <p className="text-xs text-muted-foreground">+1 (555) 123-4567</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex flex-col sm:flex-row gap-3 pt-4">
                            <Button
                                onClick={handleRefresh}
                                className="flex-1"
                            >
                                <RefreshCw className="w-4 h-4 mr-2" />
                                Refresh Page
                            </Button>
                            <Button
                                onClick={handleGoBack}
                                variant="outline"
                                className="flex-1"
                            >
                                <ArrowLeft className="w-4 h-4 mr-2" />
                                Go Back
                            </Button>
                        </div>
                    </CardContent>
                </Card>

                {/* Footer */}
                <div className="text-center mt-8 text-sm text-muted-foreground">
                    <p>If you continue to experience issues, please contact our support team.</p>
                </div>
            </div>
        </div>
    );
}
