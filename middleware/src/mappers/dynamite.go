package mappers

import (
	"encoding/json"
	"fmt"
	"strings"
)

type DynamiteJob struct {
	Slug         string   `json:"slug"`
	Url          string   `json:"url"`
	Company      string   `json:"company"`
	CompanyImage string   `json:"companyImage"`
	Title        string   `json:"title"`
	Description  string   `json:"descriptionHTML"`
	Type         string   `json:"type"`
	Category     string   `json:"primaryCategory"`
	SubCategory  string   `json:"primarySubCategory"`
	Locations    []string `json:"locations"`
	Salary       string   `json:"salary"`
	Skills       []string `json:"skills"`
	Expiry       string   `json:"expiresAt"`
}

type DynamiteResponse struct {
	JobCount int           `json:"jobCount"`
	Jobs     []DynamiteJob `json:"jobs"`
}

type DynamiteServerResponse struct {
	Error string           `json:"error"`
	Data  DynamiteResponse `json:"data"`
}

func MapDynamiteToCommon(responseJSON []byte) ([]Job, error) {
	var response DynamiteServerResponse
	err := json.Unmarshal(responseJSON, &response)
	if err != nil {
		return nil, err
	}

	if response.Data.JobCount <= 0 {
		return nil, nil
	}

	var commonJobs []Job
	for _, job := range response.Data.Jobs {

		category := job.Category
		if strings.TrimSpace(job.SubCategory) != "" {
			category = fmt.Sprintf("%s / %s", category, job.SubCategory)
		}

		commonJobs = append(
			commonJobs,
			Job{
				Source:      "Dynamite",
				Id:          job.Slug,
				Url:         job.Url,
				CompanyName: job.Company,
				CompanyLogo: job.CompanyImage,
				Title:       job.Title,
				Description: job.Description,
				Type:        job.Type,
				Category:    category,
				Locations:   job.Locations,
				Salary:      job.Salary,
				Skills:      job.Skills,
				Expires:     job.Expiry,
			},
		)
	}

	return commonJobs, nil
}
