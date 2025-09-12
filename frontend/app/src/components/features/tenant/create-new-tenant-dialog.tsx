import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle, DialogDescription } from "@/components/ui/dialog";

interface CreateNewTenantDialogProps {
    open: boolean;
    onDismiss: () => void;
}
export function CreateNewTenantDialog({ open, onDismiss }: CreateNewTenantDialogProps) {
    return (
        <Dialog open={open} onOpenChange={onDismiss}>
            <DialogContent>
                <DialogTitle className="text-2xl font-bold mb-4">Create New Tenant</DialogTitle>
                <DialogDescription className="mb-6">
                    Please provide the necessary information to create a new tenant.
                </DialogDescription>
                <div className="mt-4 flex justify-end">
                    <Button variant="outline" onClick={onDismiss}>
                        Cancel
                    </Button>
                    <Button className="ml-2" onClick={onDismiss}>
                        Create
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    )
}