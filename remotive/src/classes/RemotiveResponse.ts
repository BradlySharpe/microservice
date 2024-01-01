import { RemotiveJob } from "./RemotiveJob";
import { IRemotiveResponse } from "../interfaces/IRemoteiveResponse";


export class RemotiveResponse {

    public jobCount: number = 0;
    public jobs: RemotiveJob[] = [];

    constructor(response: IRemotiveResponse) {
        this.jobCount = response["job-count"];
        this.jobs = response.jobs.map(j => new RemotiveJob(j));
    }
}