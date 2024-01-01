package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"sync"

	"middleware/mappers"

	log "github.com/sirupsen/logrus"
)

type UpstreamResponse struct {
	Error  string `json:"error"`
	Mapper string `json:"mapper"`
}

type MiddlewareResponse struct {
	Errors []error       `json:"errors"`
	Jobs   []mappers.Job `json:"jobs"`
}

func formatError(upstreamUrl string, errorMessage string) error {
	return fmt.Errorf("upstream error from '%s'\n  - %s", upstreamUrl, errorMessage)
}

func processUpstream(upstreamUrl string) ([]mappers.Job, error) {
	resp, err := http.Get(upstreamUrl)
	if err != nil {
		return nil, formatError(upstreamUrl, fmt.Sprintf("An error occurred while making upstream request: %s", err))
	}

	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, formatError(upstreamUrl, fmt.Sprintf("Error reading upstream response: %s", err))
	}

	var upstreamResponse UpstreamResponse
	err = json.Unmarshal(body, &upstreamResponse)
	if err != nil {
		return nil, formatError(upstreamUrl, fmt.Sprintf("Error parsing the upstream response: %s", err))
	}

	if strings.TrimSpace(upstreamResponse.Error) != "" {
		return nil, formatError(upstreamUrl, fmt.Sprintf("Upstream returned an error: %s", upstreamResponse.Error))
	}

	var upstreamJobs []mappers.Job

	switch upstreamResponse.Mapper {
	case "remotive":
		upstreamJobs, err = mappers.MapRemotiveToCommon(body)
	case "dynamite":
		upstreamJobs, err = mappers.MapDynamiteToCommon(body)
	default:
		return nil, formatError(upstreamUrl, fmt.Sprintf("Unknown mapper returned: %s", upstreamResponse.Mapper))
	}

	if err != nil {
		return nil, formatError(upstreamUrl, fmt.Sprintf("Error mapping upstream jobs: %s", err))
	}

	return upstreamJobs, nil
}

func aggregateJobsFromUpstreams() ([]mappers.Job, []error) {
	var allJobs []mappers.Job
	var errors []error

	var wg sync.WaitGroup
	var mu sync.Mutex

	upstreamServers := getUpstreamServers()
	jobsChannel := make(chan []mappers.Job, len(upstreamServers))
	errorsChannel := make(chan error, len(upstreamServers))

	for _, upstreamUrl := range upstreamServers {
		wg.Add(1)
		go func(url string) {
			defer wg.Done()

			jobs, err := processUpstream(url)
			if err != nil {
				errorsChannel <- err
				return
			}

			jobsChannel <- jobs
		}(upstreamUrl)
	}

	go func() {
		wg.Wait()
		close(jobsChannel)
		close(errorsChannel)
	}()

	for jobs := range jobsChannel {
		mu.Lock()
		allJobs = append(allJobs, jobs...)
		mu.Unlock()
	}

	for err := range errorsChannel {
		mu.Lock()
		errors = append(errors, err)
		mu.Unlock()
	}

	return allJobs, errors
}

func getJobsHandler(w http.ResponseWriter, r *http.Request) {
	log.SetOutput(os.Stdout)

	jobs, errs := aggregateJobsFromUpstreams()

	if len(errs) > 0 {
		log.WithFields(
			log.Fields{
				"errors": errs,
			},
		).Info("Upstream errors occurred while fetching jobs")
	}

	response := MiddlewareResponse{
		Errors: errs,
		Jobs:   jobs,
	}

	responseJSON, err := json.Marshal(response)
	if err != nil {
		message := "An error occurred while encoding the JSON response"

		log.WithFields(
			log.Fields{
				"errors": errs,
				"jobs":   jobs,
			},
		).Error(message)

		http.Error(w, "Error encoding JSON response", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(responseJSON)
}
