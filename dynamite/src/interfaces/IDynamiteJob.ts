import { IDynamiteCategories } from "./IDynamiteCategories";
import { IDynamiteCompany } from "./IDynamiteCompany";
import { IDynamiteSalary } from "./IDynamiteSalary";

export interface IDynamiteJob {
    title: string;
    type: {
        name: {
            display: string;
        },
        slug: string;
    };
    status: string;
    slug: string;
    skills: [
        { name: string; }
    ];
    salary: IDynamiteSalary;
    primaryCategory: {
        name: string;
    };
    primarySubCategory: {
        name: string;
    };
    locationSlugs: string[];
    description: string;
    descriptionHTML: string;
    company: IDynamiteCompany;
    categories: IDynamiteCategories[];
    expiresAt: Date;
}