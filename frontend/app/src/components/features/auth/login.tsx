import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
import { useAuth } from "@/hooks/use-auth";
import { NavLink } from "react-router";



const loginSchema = z.object({
    email: z.email({ message: "Invalid email address" }),
    password: z.string()
        .min(8, { message: "Password must be at least 8 characters" })
        .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, {
            message: "Password must contain at least 1 lowercase letter, 1 uppercase letter, 1 number, and 1 symbol"
        })
});

type LoginFormInputs = z.infer<typeof loginSchema>;

export function Login() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { login } = useAuth();

    const form = useForm<LoginFormInputs>({
        resolver: zodResolver(loginSchema),
        defaultValues: {
            email: "",
            password: "",
        },
    });

    const onSubmit = async (data: LoginFormInputs) => {
        setIsLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append("email", data.email);
        formData.append("password", data.password);
        await login({
            email: data.email,
            password: data.password
        }).catch((error) => {
            setError(error.message);
        }).finally(() => {
            setIsLoading(false);
        });

    };

    return (
        <div className="flex flex-col items-center justify-center h-[calc(100vh-10rem)]">
            <Card className="w-full max-w-md shadow-lg">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">Full-Stack Fast API</CardTitle>
                    <CardDescription className="text-center text-muted-foreground">
                        Enter your email and password to access your account
                    </CardDescription>
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
                            <FormField
                                control={form.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Password</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="password"
                                                placeholder="Enter your password"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <div className="flex justify-between items-center mt-1 mb-4">
                                <div className="text-sm text-muted-foreground">Forgot your password?</div>
                                <NavLink to="/forgot-password" className="text-sm text-primary underline hover:text-primary/80">Reset here</NavLink>
                            </div>
                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? "Signing in..." : "Login"}
                            </Button>
                        </form>
                    </Form>
                    <div className="mt-6 text-center text-sm text-muted-foreground border-t pt-4">
                        Don&apos;t have an account?{' '}
                        <NavLink to="/register" className="text-primary underline hover:text-primary/80">Register</NavLink>
                    </div>
                </CardContent>
            </Card>
        </div>
    )



}