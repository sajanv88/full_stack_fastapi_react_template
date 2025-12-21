import {
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

export default function ColorField({
    control,
    name,
    label
}: {
    control: any;
    name: any;
    label: string;
}) {
    return (
        <FormField
            control={control}
            name={name}
            render={({ field }) => (
                <FormItem>
                    <FormLabel className="text-sm">{label}</FormLabel>
                    <FormControl>
                        <div className="flex items-center space-x-2">
                            <Input
                                placeholder="HSL value (e.g., 0 0% 100%)"
                                {...field}
                                className="flex-1"
                            />
                            {field.value && (
                                <div
                                    className="w-10 h-10 rounded border"
                                    style={{
                                        background: `hsl(${field.value})`
                                    }}
                                />
                            )}
                        </div>
                    </FormControl>
                    <FormMessage />
                </FormItem>
            )}
        />
    );
}