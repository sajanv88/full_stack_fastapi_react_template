import { useTenants } from "@/components/providers/tenant-provider";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogDescription, DialogHeader } from "@/components/ui/dialog";
import z from "zod";
import { Gender } from "@/components/features/auth/register";
import { useEffect, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { useAppConfig } from "@/components/providers/app-config-provider";
import { useSubdomainCheck } from "@/hooks/use-subdomain-check";
import { Alert, AlertDescription } from "@/components/ui/alert";

const tenantSchema = z.object({
    firstName: z.string()
        .min(1, { message: "First name cannot be empty" })
        .trim(),
    lastName: z.string()
        .min(1, { message: "Last name cannot be empty" })
        .trim(),
    subdomain: z.string().min(3, { message: "Subdomain cannot be empty" }).trim(),
    adminEmail: z.email({ message: "Email must be a valid email address" }),
    adminPassword: z.string()
        .min(8, { message: "Password must be at least 8 characters" })
        .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, {
            message: "Password must contain at least 1 lowercase letter, 1 uppercase letter, 1 number, and 1 symbol"
        }),
    confirmPassword: z.string()
        .min(1, { message: "Please confirm your password" }),
    gender: z.enum([Gender.MALE, Gender.FEMALE, Gender.OTHER, Gender.UNKNOWN], {
        message: "Gender must be either male, female, other, or unknown"
    })
}).refine((data) => data.adminPassword === data.confirmPassword, {
    message: "Confirm password must match password",
    path: ["confirmPassword"],
});

type TenantFormInputs = z.infer<typeof tenantSchema>;

interface CreateNewTenantDialogProps {
    open: boolean;
    onDismiss: () => void;
}
export function CreateNewTenantDialog({ open, onDismiss }: CreateNewTenantDialogProps) {
    const { onCreateNewTenant } = useTenants();
    const appConfig = useAppConfig();
    const { setSubdomain, isAvailable, isChecking, error } = useSubdomainCheck();

    const mainDomainName = appConfig.host_main_domain;
    const [isLoading, setIsLoading] = useState(false);
    const form = useForm<TenantFormInputs>({
        resolver: zodResolver(tenantSchema),
        defaultValues: {
            firstName: "",
            lastName: "",
            adminEmail: "",
            adminPassword: "",
            confirmPassword: "",
            gender: Gender.UNKNOWN,
            subdomain: "",
        },
    });

    async function onSubmit(data: TenantFormInputs) {
        try {
            setIsLoading(true);
            await onCreateNewTenant({
                first_name: data.firstName,
                last_name: data.lastName,
                admin_email: data.adminEmail,
                admin_password: data.adminPassword,
                gender: data.gender,
                subdomain: `${data.subdomain}.${mainDomainName}`,
            })
            form.reset();
            onDismiss();

        } catch (error) {
            console.error("Error creating tenant:", error);
        } finally {
            setIsLoading(false);
        }

    }
    function onDismissDialog(flag: boolean) {
        console.log("onDismissDialog called with flag:", flag);
        if (!flag) {
            form.reset();
            onDismiss();
        }
    }

    useEffect(() => {
        if (isAvailable === false) {
            form.setError("subdomain", { type: "manual", message: "This subdomain is already taken" });
        } else if (isAvailable === true) {
            form.clearErrors("subdomain");
        }
        if (error) {
            form.setError("subdomain", { type: "manual", message: error });
        }
    }, [isAvailable, error]);
    return (
        <Dialog open={open} onOpenChange={onDismissDialog}>
            <DialogContent className="sm:max-w-screen-sm">
                <DialogHeader >
                    <DialogTitle className="text-2xl font-bold mb-4">Create New Tenant</DialogTitle>
                    <DialogDescription className="mb-6">
                        Please provide the necessary information to create a new tenant.
                    </DialogDescription>
                </DialogHeader>
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

                        <section className="space-y-1">
                            <div className="flex space-x-2 items-center justify-between">
                                <FormField
                                    control={form.control}
                                    name="subdomain"
                                    render={({ field }) => (
                                        <FormItem className="w-full">
                                            <FormLabel>Subdomain</FormLabel>
                                            <FormControl>
                                                <Input
                                                    type="text"
                                                    placeholder="subdomain name"
                                                    onInput={(e: React.ChangeEvent<HTMLInputElement>) => setSubdomain(e.target.value)}
                                                    disabled={isChecking || isLoading}
                                                    {...field}
                                                />
                                            </FormControl>
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
                            {form.getFieldState("subdomain").error && (
                                <Alert variant="destructive" className="mt-4">
                                    <AlertDescription>{form.getFieldState("subdomain").error?.message}</AlertDescription>
                                </Alert>
                            )}
                        </section>


                        {/* Email */}
                        <FormField
                            control={form.control}
                            name="adminEmail"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Admin Email Address</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="email"
                                            placeholder="This will be the admin email"
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
                            name="adminPassword"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Admin Password</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="password"
                                            placeholder="This will be the admin password"
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
                                    <FormLabel>Admin Confirm Password</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="password"
                                            placeholder="Retype the password"
                                            disabled={isLoading}
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <div className="mt-4 flex justify-end">
                            <Button variant="outline" type="button" onClick={() => {
                                onDismissDialog(false);
                            }} disabled={isLoading}>
                                Cancel
                            </Button>
                            <Button className="ml-2" type="submit" disabled={isLoading}>
                                Create
                            </Button>
                        </div>
                    </form>
                </Form>

            </DialogContent>
        </Dialog>
    )
}