import { Button } from "@/components/ui/button";
import { DialogHeader, DialogFooter, Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import {
    Form, FormField, FormLabel, FormControl, FormItem, FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Gender } from "@/components/features/auth/register";
import { useForm } from "react-hook-form";
import { useState } from "react";
import { toast } from "sonner";
import { useUsers } from "@/components/providers/users-provider";



const editUserSchema = z.object({

    firstName: z.string()
        .min(1, { message: "First name cannot be empty" })
        .trim(),
    lastName: z.string()
        .min(1, { message: "Last name cannot be empty" })
        .trim(),
    gender: z.enum([Gender.MALE, Gender.FEMALE, Gender.OTHER, Gender.UNKNOWN], {
        message: "Gender must be either male, female, other, or unknown"
    })
});

type EditUserFormInputs = z.infer<typeof editUserSchema>;

interface UserEditDialogProps {
    open: boolean;
    onDismiss: () => void;
}

export function UserEditDialog({ open, onDismiss }: UserEditDialogProps) {
    const [isLoading, setIsLoading] = useState(false);
    const { onUpdateUser, selectedUser } = useUsers();

    const form = useForm<EditUserFormInputs>({
        resolver: zodResolver(editUserSchema),
        defaultValues: {
            firstName: selectedUser?.user.first_name || "",
            lastName: selectedUser?.user.last_name || "",
            gender: selectedUser?.user.gender || Gender.UNKNOWN,
        },
    });

    const onSubmit = async (data: EditUserFormInputs) => {
        console.log("Form Data Submitted: ", data);
        setIsLoading(true);
        try {
            await onUpdateUser(selectedUser?.user.id!, {
                first_name: data.firstName,
                last_name: data.lastName,
                gender: data.gender
            });

            form.reset();
            toast.success("User updated successfully!", {
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
                    <DialogTitle>Edit New User</DialogTitle>

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



                        <DialogFooter>

                            <Button type="submit" className="w-full" disabled={isLoading}>
                                {isLoading ? "Updating User..." : "Update User"}
                            </Button>
                        </DialogFooter>
                    </form>
                </Form>
            </DialogContent>
        </Dialog>
    );
}
