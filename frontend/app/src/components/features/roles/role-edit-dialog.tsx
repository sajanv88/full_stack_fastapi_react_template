import { Button } from "@/components/ui/button";
import { DialogHeader, DialogFooter, Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import {
    Form, FormField, FormLabel, FormControl, FormItem, FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { toast } from "sonner";
import { useRoles } from "@/components/providers/roles-provider";
import { Textarea } from "@/components/ui/textarea";


const editNewRoleSchema = z.object({
    name: z.string()
        .min(2, { message: "Name must be at least 2 characters long" })
        .max(20, { message: "Name must be at most 20 characters long" })
        .trim(),
    description: z.string()
        .min(10, { message: "Description must be at least 10 characters long" })
        .max(200, { message: "Description must be at most 200 characters long" })
        .trim(),

});

type EditRoleFormInputs = z.infer<typeof editNewRoleSchema>;

interface RoleEditDialogProps {
    open: boolean;
    onDismiss: () => void;
}

export function RoleEditDialog({ open, onDismiss }: RoleEditDialogProps) {
    const [isLoading, setIsLoading] = useState(false);
    const { onUpdateRole, selectedRole } = useRoles();

    const form = useForm<EditRoleFormInputs>({
        resolver: zodResolver(editNewRoleSchema),
        defaultValues: {
            name: selectedRole?.role.name || "",
            description: selectedRole?.role.description || "",
        },
    });

    const onSubmit = async (data: EditRoleFormInputs) => {
        console.log("Form Data Submitted: ", data);
        setIsLoading(true);
        try {
            await onUpdateRole(selectedRole?.role.id!, {
                name: data.name,
                description: data.description,
            });

            form.reset();
            toast.success("Role updated successfully!", {
                duration: 5000,
                position: "top-right",
                richColors: true,
            });
            form.reset();
            toast.success("Role updated successfully!", {
                duration: 5000,
                position: "top-right",
                richColors: true,
            });
            onDismiss();

        } catch (error) {
            toast.error("User update failed. Please try again.", {
                duration: 5000,
                position: "top-right",
                richColors: true,
            });
        } finally {
            setIsLoading(false);

        }

    };

    function onDismissDialog(flag: boolean) {
        console.log("onDismissDialog called with flag:", flag);
        if (!flag) onDismiss();
    }
    return (

        <Dialog open={open} onOpenChange={onDismissDialog} modal>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Edit Role</DialogTitle>

                </DialogHeader>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
                        {/* Name */}
                        <FormField
                            control={form.control}
                            name="name"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Role Name</FormLabel>
                                    <FormControl>
                                        <Input
                                            type="text"
                                            placeholder="Enter the role name"
                                            disabled={isLoading}
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        {/* Description */}
                        <FormField
                            control={form.control}
                            name="description"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Role Description</FormLabel>
                                    <FormControl>
                                        <Textarea
                                            placeholder="Enter the role description"
                                            disabled={isLoading}
                                            {...field}
                                        />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />

                        <DialogFooter>

                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? "Updating Role..." : "Update Role"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog >
    );
}
