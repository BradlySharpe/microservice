import { IRemotiveJob } from "../interfaces/IRemotiveJob";


export class RemotiveJob {
    id: number;
    url: string;
    title: string;
    company_name: string;
    company_logo: string;
    category: string;
    job_type: string;
    publication_date: Date;
    candidate_required_location: string[];
    salary: string;
    description: string;
    tags: string[];

    constructor(job: IRemotiveJob) {
        this.id = job.id;
        this.url = job.url;
        this.title = job.title;
        this.company_name = job.company_name;
        this.company_logo = job.company_logo;
        this.category = job.category;
        this.job_type = job.job_type;
        this.publication_date = new Date(job.publication_date);
        this.candidate_required_location = `${job.candidate_required_location}`.split(',').map(l => `${l}`.trim());
        this.salary = job.salary;
        this.description = job.description;
        this.tags = `${job.tags}`.split(',').map(t => `${t}`.trim());
    }
}