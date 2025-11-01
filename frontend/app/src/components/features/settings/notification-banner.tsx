import { useEffect, useState } from "react";
import { useAuthContext } from "@/components/providers/auth-provider";
import { getApiClient } from "@/lib/utils";
import { NotificationBannerSettingDto } from "@/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import {
    Bell,
    RefreshCw,
    Save,
    AlertCircle,
    CheckCircle2,
    Info,
} from "lucide-react";
import { ShowScreenLoader } from "@/components/shared/show-screen-loader";
import { useAppConfig } from "@/components/providers/app-config-provider";

const notificationSchema = z.object({
    is_enabled: z.boolean(),
    message: z.string().min(1, "Message is required").max(500, "Message must be less than 500 characters"),
});

type NotificationForm = z.infer<typeof notificationSchema>;

export function NotificationBanner() {
    const { accessToken } = useAuthContext();
    const { reloadAppConfig } = useAppConfig();
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [currentNotification, setCurrentNotification] = useState<NotificationBannerSettingDto | null>(null);

    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors, isDirty },
    } = useForm<NotificationForm>({
        resolver: zodResolver(notificationSchema),
        defaultValues: {
            is_enabled: false,
            message: "",
        },
    });

    const isEnabled = watch("is_enabled");
    const message = watch("message");

    const fetchNotificationBanner = async () => {
        if (!accessToken) return;
        try {
            setLoading(true);
            const response = await getApiClient(accessToken).notifications.getNotificationBannerApiV1NotificationsBannerGet();
            setCurrentNotification(response);
            reset({
                is_enabled: response.is_enabled,
                message: response.message || "",
            });
        } catch (error) {
            console.error("Error fetching notification banner:", error);
            // If no notification exists yet, keep defaults
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (accessToken) {
            fetchNotificationBanner();
        }
    }, [accessToken]);

    const onSubmit = async (data: NotificationForm) => {
        if (!accessToken) return;
        try {
            setSubmitting(true);

            if (currentNotification?.id) {
                // Update existing
                await getApiClient(accessToken).notifications.updateNotificationBannerApiV1NotificationsBannerIdPut({
                    id: currentNotification.id,
                    requestBody: {
                        is_enabled: data.is_enabled,
                        message: data.message || null,
                    },
                });
                toast.success("Notification banner updated successfully", { richColors: true, position: "top-right" });
            } else {
                // Create new
                await getApiClient(accessToken).notifications.createNotificationBannerApiV1NotificationsBannerPost({
                    requestBody: {
                        is_enabled: data.is_enabled,
                        message: data.message || null,
                    },
                });
                toast.success("Notification banner created successfully", { richColors: true, position: "top-right" });
            }

            Promise.all([fetchNotificationBanner(), reloadAppConfig()]);
        } catch (error) {
            console.error("Error saving notification banner:", error);
            toast.error("Failed to save notification banner", { richColors: true, position: "top-right" });
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <ShowScreenLoader message="Loading notification settings..." />
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
                        <Bell className="h-6 w-6" />
                        Notification Banner
                    </h2>
                    <p className="text-muted-foreground mt-1">
                        Manage the notification banner displayed to users across your application
                    </p>
                </div>
                <Button onClick={fetchNotificationBanner} variant="outline">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Refresh
                </Button>
            </div>



            {/* Configuration Form */}
            <form onSubmit={handleSubmit(onSubmit)}>
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Bell className="h-5 w-5" />
                            {currentNotification ? "Update Notification Banner" : "Create Notification Banner"}
                        </CardTitle>
                        <CardDescription>
                            Configure the message and visibility of the notification banner
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* Enable/Disable Toggle */}
                        <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                            <div className="space-y-0.5">
                                <Label htmlFor="is_enabled" className="text-base font-medium">
                                    Enable Banner
                                </Label>
                                <p className="text-sm text-muted-foreground">
                                    Make the notification banner visible to all users
                                </p>
                            </div>
                            <Switch
                                id="is_enabled"
                                checked={isEnabled}
                                onCheckedChange={(checked) => setValue("is_enabled", checked, { shouldDirty: true })}
                            />
                        </div>

                        <Separator />

                        {/* Message Input */}
                        <div className="space-y-2">
                            <Label htmlFor="message">
                                Banner Message <span className="text-destructive">*</span>
                            </Label>
                            <Textarea
                                id="message"
                                placeholder="Enter your notification message here..."
                                rows={4}
                                maxLength={500}
                                {...register("message")}
                            />
                            <div className="flex items-center justify-between">
                                <div>
                                    {errors.message && (
                                        <p className="text-sm text-destructive">{errors.message.message}</p>
                                    )}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    {message.length}/500 characters
                                </p>
                            </div>
                            <p className="text-xs text-muted-foreground">
                                This message will be displayed at the top of the application when the banner is enabled
                            </p>
                        </div>

                        <Separator />

                        {/* Preview */}
                        {message && (
                            <div className="space-y-2">
                                <Label>Preview</Label>
                                <Alert className={isEnabled ? "border-blue-200 bg-blue-50 dark:bg-blue-950" : ""}>
                                    <Info className="h-4 w-4" />
                                    <AlertDescription>
                                        {message}
                                    </AlertDescription>
                                </Alert>
                                <p className="text-xs text-muted-foreground">
                                    This is how the banner will appear to users
                                </p>
                            </div>
                        )}

                        {/* Info Box */}
                        <Alert>
                            <Info className="h-4 w-4" />
                            <AlertDescription>
                                <strong>Note:</strong> The notification banner will be visible across all pages when
                                enabled. Make sure your message is clear and concise.
                            </AlertDescription>
                        </Alert>

                        {/* Action Buttons */}
                        <div className="flex flex-col sm:flex-row gap-3 pt-4">
                            <Button type="submit" className="flex-1" disabled={submitting || !isDirty}>
                                {submitting ? (
                                    <>
                                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4 mr-2" />
                                        {currentNotification ? "Update Banner" : "Create Banner"}
                                    </>
                                )}
                            </Button>
                            <Button
                                type="button"
                                variant="outline"
                                className="flex-1"
                                onClick={() => reset()}
                                disabled={submitting || !isDirty}
                            >
                                Reset Changes
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </form>

            {/* Information Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                            <Bell className="h-5 w-5 text-muted-foreground mt-0.5" />
                            <div>
                                <p className="text-sm font-medium">Banner Status</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {isEnabled ? "Active" : "Inactive"}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="h-5 w-5 text-muted-foreground mt-0.5" />
                            <div>
                                <p className="text-sm font-medium">Message Length</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {message.length} characters
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-start gap-3">
                            <CheckCircle2 className="h-5 w-5 text-muted-foreground mt-0.5" />
                            <div>
                                <p className="text-sm font-medium">Changes</p>
                                <p className="text-xs text-muted-foreground mt-1">
                                    {isDirty ? "Unsaved changes" : "All changes saved"}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
