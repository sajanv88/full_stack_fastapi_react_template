export interface IResponseData<T> {
    items: T[];
    skip: number;
    limit: number;
    total: number;
    hasPrevious: boolean;
    hasNext: boolean;
}