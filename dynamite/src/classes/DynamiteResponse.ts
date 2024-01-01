import { IDynamiteResponse } from "../interfaces/IDynamiteResponse";
import { DynamiteJob } from "./DynamiteJob";


export class DynamiteResponse {

    public jobCount: number = 0;
    public jobs: DynamiteJob[];

    constructor(response: IDynamiteResponse) {
        this.jobs = response.hits.map(j => new DynamiteJob(j));

        if (this.jobs != null)
            this.jobCount = this.jobs.length;
    }
    
}