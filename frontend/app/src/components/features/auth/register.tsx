import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { NavLink, useNavigate } from "react-router";
import { useAuth } from "@/hooks/use-auth";
import { Logo } from "@/components/shared/logo";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { Label } from "@/components/ui/label";

// Gender enum matching the backend
export const Gender = {
    MALE: 'male',
    FEMALE: 'female',
    OTHER: 'other',
    UNKNOWN: 'prefer_not_to_say',
} as const;

// Zod schema matching the SignupDto validation
const signupSchema = z.object({
    firstName: z.string()
        .min(1, { message: "First name cannot be empty" })
        .trim(),
    lastName: z.string()
        .min(1, { message: "Last name cannot be empty" })
        .trim(),
    subdomain: z.string().optional(),
    email: z.email({ message: "Email must be a valid email address" }),
    password: z.string()
        .min(8, { message: "Password must be at least 8 characters" })
        .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, {
            message: "Password must contain at least 1 lowercase letter, 1 uppercase letter, 1 number, and 1 symbol"
        }),
    confirmPassword: z.string()
        .min(1, { message: "Please confirm your password" }),
    gender: z.enum([Gender.MALE, Gender.FEMALE, Gender.OTHER, Gender.UNKNOWN], {
        message: "Gender must be either male, female, other, or unknown"
    })
}).refine((data) => data.password === data.confirmPassword, {
    message: "Confirm password must match password",
    path: ["confirmPassword"],
});

type SignupFormInputs = z.infer<typeof signupSchema>;

export default function Register() {
    const [isLoading, setIsLoading] = useState(false);
    const { register } = useAuth();
    const appConfig = useAppConfig();

    const isMultiTenancyEnabled = appConfig.is_multi_tenant_enabled;
    const mainDomainName = appConfig.host_main_domain;

    const form = useForm<SignupFormInputs>({
        resolver: zodResolver(signupSchema),
        defaultValues: {
            firstName: "",
            lastName: "",
            email: "",
            password: "",
            confirmPassword: "",
            gender: Gender.UNKNOWN,
            subdomain: "",
        },
    });

    const onSubmit = async (data: SignupFormInputs) => {
        setIsLoading(true);
        try {
            if (isMultiTenancyEnabled && (!data.subdomain || data.subdomain.trim() === "")) {
                form.setError("subdomain", { message: "Subdomain is required" });
                return;
            }
            await register({
                email: data.email,
                password: data.password,
                first_name: data.firstName,
                last_name: data.lastName,
                gender: data.gender,
                sub_domain: isMultiTenancyEnabled ? `${data.subdomain}.${mainDomainName}` : ""
            });
            toast.success("Registration successful! Please check your email for verification.", {
                duration: 5000,
                position: "top-center",
                richColors: true
            });

        } catch (error) {
            toast.error("Registration failed. Please try again.", {
                duration: 5000,
                position: "top-center",
                richColors: true
            });
        } finally {
            setIsLoading(false);

        }

    };



    return (
        <div className="flex flex-col items-center justify-center h-[calc(100vh-10rem)]">
            <Card className="w-full max-w-md shadow-lg">
                <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">
                        <Logo className="justify-center pb-5" />
                    </CardTitle>
                    <CardDescription className="text-center text-muted-foreground">
                        Enter your information to create a new account
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                            {/* First Name */}
                            <FormField
                                control={form.control}
                                name="firstName"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>First Name</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="text"
                                                placeholder="Enter your first name"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            {/* Last Name */}
                            <FormField
                                control={form.control}
                                name="lastName"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Last Name</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="text"
                                                placeholder="Enter your last name"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            {isMultiTenancyEnabled && (
                                <div className="flex space-x-2 items-center">
                                    <FormField
                                        control={form.control}
                                        name="subdomain"
                                        render={({ field }) => (
                                            <FormItem>
                                                <FormLabel>Subdomain</FormLabel>
                                                <FormControl>
                                                    <Input
                                                        type="text"
                                                        placeholder="subdomain name"
                                                        disabled={isLoading}
                                                        {...field}
                                                    />
                                                </FormControl>
                                                <FormMessage />
                                            </FormItem>
                                        )}

                                    />
                                    <span>
                                        <Label htmlFor="base-domain" className="pb-3">Base Domain</Label>
                                        <Input
                                            id="base-domain"
                                            type="text"
                                            value={`.${mainDomainName}`}
                                            disabled={true}

                                        />
                                    </span>
                                </div>
                            )}


                            {/* Email */}
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

                            {/* Gender */}
                            <FormField
                                control={form.control}
                                name="gender"
                                render={({ field }) => (
                                    <FormItem className="flex flex-row items-center gap-4">
                                        <FormLabel className="w-32 mb-0">Gender</FormLabel>
                                        <div className="flex-1">
                                            <Select onValueChange={field.onChange} defaultValue={field.value} disabled={isLoading}>
                                                <FormControl>
                                                    <SelectTrigger className="w-full">
                                                        <SelectValue placeholder="Select your gender" className="w-full" />
                                                    </SelectTrigger>
                                                </FormControl>
                                                <SelectContent>
                                                    <SelectItem value={Gender.MALE}>Male</SelectItem>
                                                    <SelectItem value={Gender.FEMALE}>Female</SelectItem>
                                                    <SelectItem value={Gender.OTHER}>Other</SelectItem>
                                                    <SelectItem value={Gender.UNKNOWN}>Prefer not to say</SelectItem>
                                                </SelectContent>
                                            </Select>
                                            <FormMessage />
                                        </div>
                                    </FormItem>
                                )}
                            />

                            {/* Password */}
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

                            {/* Confirm Password */}
                            <FormField
                                control={form.control}
                                name="confirmPassword"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Confirm Password</FormLabel>
                                        <FormControl>
                                            <Input
                                                type="password"
                                                placeholder="Confirm your password"
                                                disabled={isLoading}
                                                {...field}
                                            />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />

                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? "Creating Account..." : "Create Account"}
                            </Button>
                        </form>
                    </Form>
                    <div className="mt-6 text-center text-sm text-muted-foreground border-t pt-4">
                        Already have an account?{' '}
                        <NavLink to="/login" className="text-primary underline hover:text-primary/80">
                            Log in
                        </NavLink>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}