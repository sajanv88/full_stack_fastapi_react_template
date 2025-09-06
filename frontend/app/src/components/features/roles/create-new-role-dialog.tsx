import { Button } from "@/components/ui/button";
import { DialogHeader, DialogFooter, Dialog, DialogContent, DialogDescription, DialogTitle } from "@/components/ui/dialog";
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



const createNewRoleSchema = z.object({
    name: z.string()
        .min(2, { message: "Name must be at least 2 characters long" })
        .max(20, { message: "Name must be at most 20 characters long" })
        .trim(),
    description: z.string()
        .min(10, { message: "Description must be at least 10 characters long" })
        .max(200, { message: "Description must be at most 200 characters long" })
        .trim(),

});

type CreateNewRoleFormInputs = z.infer<typeof createNewRoleSchema>;

interface CreateNewRoleDialogProps {
    open: boolean;
    onDismiss: () => void;
}

export function CreateNewRoleDialog({ open, onDismiss }: CreateNewRoleDialogProps) {
    const [isLoading, setIsLoading] = useState(false);
    const { onCreateNewRole } = useRoles();

    const form = useForm<CreateNewRoleFormInputs>({
        resolver: zodResolver(createNewRoleSchema),
        defaultValues: {
            name: "",
            description: "",
        },
    });

    const onSubmit = async (data: CreateNewRoleFormInputs) => {
        console.log("Form Data Submitted: ", data);
        setIsLoading(true);
        try {
            await onCreateNewRole({
                name: data.name,
                description: data.description,
            });


            form.reset();
            toast.success("Role created successfully!", {
                duration: 5000,
                position: "top-center",
                richColors: true,
            });
            onDismiss();

        } catch (error) {
            toast.error("Role creation failed. Please try again.", {
                duration: 5000,
                position: "top-center",
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
                    <DialogTitle>Create New Role</DialogTitle>
                    <DialogDescription>
                        Fill in the details to create a new role.
                    </DialogDescription>
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
                                {isLoading ? "Creating Role..." : "Create New Role"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog >
    );
}
