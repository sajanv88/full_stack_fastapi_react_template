import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { NavLink } from "react-router";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Logo } from "@/components/shared/logo";
import { getApiClient } from "@/lib/utils";
import { toast } from "sonner";



const passwordResetSchema = z.object({
    email: z.email({ message: "Invalid email address" }),

});

type passwordResetSchemaInput = z.infer<typeof passwordResetSchema>;

export function PasswordResetRequest() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const apiClient = getApiClient();
    const form = useForm<passwordResetSchemaInput>({
        resolver: zodResolver(passwordResetSchema),
        defaultValues: {
            email: "",
        },
    });


    const onSubmit = async (data: passwordResetSchemaInput) => {
        setIsLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append("email", data.email);
        try {
            await apiClient.account.passwordResetRequestApiV1AccountPasswordResetRequestPost({
                requestBody: {
                    email: data.email
                }
            })
            toast.success("If the email is registered, you will receive password reset instructions.", { duration: 5000, position: "top-center", richColors: true });
        } catch (error) {
            setError("Invalid email");
        }
        finally {
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
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="email"
                                                placeholder="Enter your email"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />


                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? "Requesting..." : "Request Password Reset"}
                            </Button>
                        </form>
                    </Form>
                    <div className="mt-6 text-center text-sm text-muted-foreground border-t pt-4">
                        Don&apos;t have an account?{' '}
                        <NavLink to="/register" className="text-primary underline hover:text-primary/80">Register</NavLink>
                    </div>


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