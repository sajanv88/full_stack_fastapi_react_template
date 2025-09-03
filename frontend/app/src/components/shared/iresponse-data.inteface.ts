export interface IResponseData<T> {
    items: T[];
    totalRecords: number;
    paginate: {
        limit?: number;
        offset?: number;
        sort?: string;
        filter?: string;
    };
}