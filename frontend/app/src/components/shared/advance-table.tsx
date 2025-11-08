"use client";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    useReactTable,
} from "@tanstack/react-table";
import { useEffect, useMemo, useState } from "react";
import {
    Pagination,
    PaginationContent,
    PaginationItem,
} from "@/components/ui/pagination";
import { Button } from "@/components/ui/button";
import {
    ChevronLeftIcon,
    ChevronRightIcon,
    ArrowLeftIcon,
    ArrowRightIcon
} from "lucide-react";
import { useSearchParams } from "react-router";
import { cn } from "@/lib/utils";
import type { IResponseData } from "@/components/shared/iresponse-data.inteface";
import { Loading } from "@/components/shared/loading";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup } from "@/components/ui/select";
import { IconFilter } from "@tabler/icons-react"
interface Props<T> {
    data: IResponseData<T>;
    columns: ColumnDef<T, any>[];
    hasBottomBorder?: boolean;
    loading?: boolean;
    errorMsg?: string;
    dropdownActions?: {
        options: Array<{ name: string; value: string }>;
    }
}

const DEFAULT_PAGE_LIMIT = 10;

export default function AdvanceTable<T>({
    data,
    columns,
    hasBottomBorder,
    loading,
    errorMsg,
    dropdownActions
}: Props<T>) {

    const [searchParams, setSearchParams] = useSearchParams();
    function onDropdownChange(value: string) {
        // Handle dropdown action change
        console.log("Selected action:", value);
        searchParams.set("action", value);
        if (value === "all") {
            searchParams.delete("action");
        }
        setSearchParams(searchParams);
    }
    const currentPage = useMemo(
        () => Number(searchParams.get("skip")),
        [searchParams],
    );
    const pageLimit = useMemo(
        () => Number(searchParams.get("limit")),
        [searchParams],
    );

    const selectedAction = useMemo(
        () => searchParams.get("action") || "all",
        [searchParams],
    );

    const limit = pageLimit === 0 ? DEFAULT_PAGE_LIMIT : pageLimit;

    const { items, total } = data;
    const totalPage = Math.ceil(total / limit);
    const [pagination, setPagination] = useState<{
        pageIndex: number;
        pageSize: number;
    }>({
        pageIndex: currentPage,
        pageSize: limit,
    });
    const table = useReactTable<T>({
        data: items,
        columns,
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
        pageCount: totalPage,
        onPaginationChange: setPagination,
        state: {
            pagination,
        },
    });

    useEffect(() => {
        if (pagination.pageIndex !== Number(currentPage)) {
            if (searchParams.get("action") && dropdownActions) {
                setSearchParams({ 'skip': pagination.pageIndex.toString(), 'limit': limit.toString(), 'action': searchParams.get("action")! });
            }
            else {
                setSearchParams({ 'skip': pagination.pageIndex.toString(), 'limit': limit.toString() });
            }
        }
    }, [pagination.pageIndex]);

    const showPagination = items.length < total;
    const renderEmptyState = () => {
        if (items.length === 0 && total === 0 && !loading) {
            return (
                <div className="grid place-items-center place-content-center h-40">
                    {errorMsg ? errorMsg : "No Records"}
                </div>
            );
        }
        if (loading) {
            return (
                <div className="grid place-items-center place-content-center h-40">
                    <Loading variant="dots" size="md" text="Loading data..." />
                </div>
            );
        }
        return <></>;
    };

    return (
        <div className="shadow max-w-[calc(100vw-1rem)] md:max-w-full overflow-hidden rounded-md border">
            {dropdownActions && (
                <div className="p-4 flex justify-end">
                    <Select onValueChange={onDropdownChange} defaultValue={selectedAction}>
                        <SelectTrigger className="w-[180px] ">
                            <IconFilter className="w-4 h-4" />
                            <SelectValue placeholder="Actions" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectGroup>
                                {dropdownActions.options.map((option) => (
                                    <SelectItem key={option.value} value={option.value}>
                                        {option.name}
                                    </SelectItem>
                                ))}
                                <SelectItem value="all">All</SelectItem>
                            </SelectGroup>
                        </SelectContent>
                    </Select>
                </div>
            )}
            <Table>
                <TableHeader>
                    {table.getHeaderGroups().map((headerGroup) => {
                        return (
                            <TableRow key={headerGroup.id}>
                                {headerGroup.headers.map((header) => {
                                    return (
                                        <TableHead key={header.id}>
                                            <span className="block truncate">
                                                {header.isPlaceholder
                                                    ? null
                                                    : flexRender(
                                                        header.column.columnDef.header,
                                                        header.getContext(),
                                                    )}
                                            </span>
                                        </TableHead>
                                    );
                                })}
                            </TableRow>
                        );
                    })}
                </TableHeader>
                <TableBody>
                    {table.getRowModel().rows.map((row) => {
                        if (loading) return null;
                        return (
                            <TableRow
                                key={row.id}
                                className={cn({
                                    "border-b": hasBottomBorder,
                                })}
                            >
                                {row.getVisibleCells().map((cell) => {
                                    return (
                                        <TableCell key={cell.id}>
                                            <span className="block truncate">
                                                {flexRender(
                                                    cell.column.columnDef.cell,
                                                    cell.getContext(),
                                                )}
                                            </span>
                                        </TableCell>
                                    );
                                })}
                            </TableRow>
                        );
                    })}
                </TableBody>
            </Table>
            {renderEmptyState()}
            {showPagination && (
                <div className="pt-3 pb-3">
                    <Pagination>
                        <PaginationContent>
                            <PaginationItem>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    onClick={() => table.firstPage()}
                                    disabled={!table.getCanPreviousPage()}
                                    aria-disabled={!table.getCanPreviousPage()}
                                >
                                    <ArrowLeftIcon />
                                </Button>
                            </PaginationItem>
                            <PaginationItem>
                                <Button
                                    size="icon"
                                    variant="outline"
                                    onClick={() => table.previousPage()}
                                    disabled={!table.getCanPreviousPage()}
                                    aria-disabled={!table.getCanPreviousPage()}
                                >
                                    <ChevronLeftIcon />
                                </Button>
                            </PaginationItem>
                            <PaginationItem>
                                <span className="flex pl-2 pr-2 text-sm">
                                    Page {pagination.pageIndex + 1} of {totalPage}
                                </span>
                            </PaginationItem>
                            <PaginationItem>
                                <Button
                                    size="icon"
                                    variant="outline"
                                    onClick={() => table.nextPage()}
                                    disabled={!table.getCanNextPage()}
                                    aria-disabled={!table.getCanNextPage()}
                                >
                                    <ChevronRightIcon />
                                </Button>
                            </PaginationItem>
                            <PaginationItem>
                                <Button
                                    variant="outline"
                                    size="icon"
                                    onClick={() => table.lastPage()}
                                    disabled={!table.getCanNextPage()}
                                    aria-disabled={!table.getCanNextPage()}
                                >
                                    <ArrowRightIcon />
                                </Button>
                            </PaginationItem>
                        </PaginationContent>
                    </Pagination>
                </div>
            )}
        </div>
    );
}