package mappers

import (
	"encoding/json"
	"strconv"
)

type RemotiveJob struct {
	Id              int      `json:"id"`
	Url             string   `json:"url"`
	CompanyName     string   `json:"company_name"`
	CompanyLogo     string   `json:"company_logo"`
	Title           string   `json:"title"`
	Description     string   `json:"description"`
	Type            string   `json:"job_type"`
	Category        string   `json:"category"`
	PublicationDate string   `json:"publication_date"`
	Locations       []string `json:"candidate_required_location"`
	Salary          string   `json:"salary"`
	Tags            []string `json:"tags"`
}

type RemotiveResponse struct {
	JobCount int           `json:"jobCount"`
	Jobs     []RemotiveJob `json:"jobs"`
}

type RemotiveServerResponse struct {
	Error string           `json:"error"`
	Data  RemotiveResponse `json:"data"`
}

func MapRemotiveToCommon(responseJSON []byte) ([]Job, error) {
	var response RemotiveServerResponse
	err := json.Unmarshal(responseJSON, &response)
	if err != nil {
		return nil, err
	}

	if response.Data.JobCount <= 0 {
		return nil, nil
	}

	var commonJobs []Job
	for _, job := range response.Data.Jobs {
		commonJobs = append(
			commonJobs,
			Job{
				Source:      "Remotive",
				Id:          strconv.Itoa(job.Id),
				Url:         job.Url,
				CompanyName: job.CompanyName,
				CompanyLogo: job.CompanyLogo,
				Title:       job.Title,
				Description: job.Description,
				Type:        job.Type,
				Category:    job.Category,
				Published:   job.PublicationDate,
				Locations:   job.Locations,
				Salary:      job.Salary,
				Tags:        job.Tags,
			},
		)
	}

	return commonJobs, nil
}
