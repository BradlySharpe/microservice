import { IRemotiveJob } from "./IRemotiveJob";

export interface IRemotiveResponse {
    "job-count": number;
    jobs: IRemotiveJob[];
}