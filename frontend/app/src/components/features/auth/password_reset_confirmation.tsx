import { useState } from 'react';
import { NavLink, useNavigate, useSearchParams } from 'react-router'
import z from 'zod';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Logo } from "@/components/shared/logo";
import { getApiClient } from "@/lib/utils";
import { toast } from "sonner";



const passwordResetConfirmationSchema = z.object({
    password: z.string()
        .min(8, { message: "Password must be at least 8 characters" })
        .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, {
            message: "Password must contain at least 1 lowercase letter, 1 uppercase letter, 1 number, and 1 symbol"
        }),
    confirmPassword: z.string()
        .min(1, { message: "Please confirm your password" })
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords must match",
    path: ["confirmPassword"]
});

type PasswordResetConfirmationFormInputs = z.infer<typeof passwordResetConfirmationSchema>;

export function PasswordResetConfirmation() {
    const [searchParams] = useSearchParams();
    const userId = searchParams.get('user_id');
    const token = searchParams.get('token');
    const tenantId = searchParams.get('tenant_id');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const apiClient = getApiClient();
    const navigate = useNavigate();

    const form = useForm<PasswordResetConfirmationFormInputs>({
        resolver: zodResolver(passwordResetConfirmationSchema),
        defaultValues: {
            password: "",
        },
    });

    const onSubmit = async (data: PasswordResetConfirmationFormInputs) => {
        setIsLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append("password", data.password);
        if (!userId || !token) {
            setError("Invalid password reset link");
            setIsLoading(false);
            return;
        }
        try {
            const response = await apiClient.account.passwordResetConfirmApiV1AccountPasswordResetConfirmationPost({
                userId,
                token,
                tenantId,
                requestBody: {
                    new_password: data.password
                }
            });
            toast.success(response.message || "Password has been reset successfully.",
                { duration: 5000, position: "top-center", richColors: true, description: "Redirecting to login..." });
            setTimeout(() => {
                navigate("/login");
            }, 1000);

        } catch (error) {
            setError("Failed to reset password. The link may be invalid or expired.");
        } finally {
            setIsLoading(false);
        }


    };
    return (
        <div className="flex flex-col items-center justify-center h-[calc(100vh-10rem)]">

            <Card className="w-full max-w-md shadow-lg">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">
                        <Logo className="justify-center" showText={false} size="sm" />
                    </CardTitle>

                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="password"
                                                placeholder="Enter your new password"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={form.control}
                                name="confirmPassword"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Confirm Password</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="password"
                                                placeholder="Confirm your new password"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <div className="flex justify-between items-center mt-1 mb-4">
                                <div className="text-sm text-muted-foreground">Failed to reset password.</div>
                                <NavLink to="/forgot-password" className="text-sm text-primary underline hover:text-primary/80">Request Again</NavLink>
                            </div>
                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? "Saving..." : "Confirm"}
                            </Button>
                        </form>
                    </Form>
                    <CardFooter className="p-0 mt-4">
                        {error && (
                            <Alert variant="destructive">
                                <AlertTitle>Error</AlertTitle>
                                <AlertDescription>{error}</AlertDescription>
                            </Alert>
                        )}
                    </CardFooter>
                </CardContent>
            </Card>

        </div>
    )
}