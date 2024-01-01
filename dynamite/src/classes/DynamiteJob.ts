import { IDynamiteCategories } from "../interfaces/IDynamiteCategories";
import { IDynamiteCompany } from "../interfaces/IDynamiteCompany";
import { IDynamiteJob } from "../interfaces/IDynamiteJob";
import { IDynamiteSalary } from "../interfaces/IDynamiteSalary";

interface ICategory {
    category: string;
    subcategory: string;
}

export class DynamiteJob {    
    title: string;
    type: string;
    status: string;
    slug: string;
    skills: string[];
    salary: string;
    primaryCategory: string;
    primarySubCategory: string;
    locations: string[];
    description: string;
    descriptionHTML: string;
    company: string;
    companySlug: string;
    companyUrl: string;
    companyImage: string;
    categories: ICategory[];
    url: string;
    expiresAt: Date;

    constructor(job: IDynamiteJob) {
        this.title = job.title;
        this.type = job.type && job.type.name ? job.type.name.display : null;
        this.status = job.status;
        this.slug = job.slug;
        this.skills = job.skills ? job.skills.map(s => s.name) : [];
        this.salary = DynamiteJob.mapSalary(job.salary);
        this.primaryCategory = job.primaryCategory ? job.primaryCategory.name : "";
        this.primarySubCategory = job.primarySubCategory ? job.primarySubCategory.name : "";
        this.locations = job.locationSlugs;
        this.description = job.description;
        this.descriptionHTML = job.descriptionHTML;
        this.company = job.company ? job.company.name : "";
        this.companySlug = job.company ? job.company.usernameLow : "";
        this.companyUrl = job.company ? job.company.companyUrl : "";
        this.companyImage = DynamiteJob.mapCompanyImage(job.company);
        this.categories = DynamiteJob.mapCategories(job.categories);
        this.url = DynamiteJob.mapJobUrl(this);
        this.expiresAt = new Date(job.expiresAt);
    }

    private static mapSalary(salary: IDynamiteSalary) {
        if (salary == null)
            return "";

        let result = "";
        if (salary.from > 0)
            result += `$${salary.from}`;

        if (salary.to) {
            if (result.length > 0)
                result += " - ";

            result += `$${salary.to}`;
        }

        if (salary.currency && salary.currency.length > 0)
            result += ` (${salary.currency})`;

        if (salary.type && salary.type.length > 0)
            result += ` ${salary.type}`;

        return result;
    }

    private static mapCompanyImage(company: IDynamiteCompany) {
        if (company == null || company.icon == null || !company.icon.hasIcon)
            return "";

        // Return the largest size image available
        const sizes = [ "lg", "md", "sm", "xs" ];

        for (const index in sizes) {
            const size = sizes[index];
            if (Object.prototype.hasOwnProperty.call(company.icon, size)) {
                if (company.icon[size].length > 0)
                    return company.icon[size];                
            }
        }

        return "";
    }

    private static mapCategories(categories: IDynamiteCategories[]) {
        if (categories == null)
            return [];

        return categories.map(c => ({
            category: c.category ? c.category.name : null,
            subcategory: c.subcategory ? c.subcategory.name : null,
        }))
    }

    private static mapJobUrl(job: DynamiteJob) {
        if (job.companySlug.length <= 0 || job.slug.length <= 0)
            return "";

        return `https://dynamitejobs.com/company/${job.companySlug}/remote-job/${job.slug}`
    }
}