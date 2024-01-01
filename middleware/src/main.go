package main

import (
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"

	log "github.com/sirupsen/logrus"
)

type RequiredEnvVar struct {
	Key  string
	Type string
}

var requiredEnvVars = []RequiredEnvVar{
	{Key: "API_PORT", Type: "number"},
	{Key: "UPSTREAM_HOSTS", Type: "string"},
}

func ensureEnvironmentVariablesAreConfigured() {
	var errors []string

	for _, variable := range requiredEnvVars {
		value, exists := os.LookupEnv(variable.Key)

		if !exists {
			errors = append(errors, fmt.Sprintf("  - %s is not configured", variable.Key))
			continue
		}

		switch variable.Type {
		case "string":
			if value == "" || strings.TrimSpace(value) == "" {
				errors = append(errors, fmt.Sprintf("  - %s is not configured", variable.Key))
			}
		case "number":
			if value == "" || strings.TrimSpace(value) == "" {
				errors = append(errors, fmt.Sprintf("  - %s is not configured", variable.Key))
				continue
			}

			if _, err := strconv.Atoi(value); err != nil {
				errors = append(errors, fmt.Sprintf("  - %s is not set to a valid number: '%s'", variable.Key, value))
			}
		default:
			errors = append(errors, fmt.Sprintf("  - Unknown type '%s' for variable: %s", variable.Type, variable.Key))
		}
	}

	if len(errors) > 0 {
		log.WithFields(
			log.Fields{
				"Errors": errors,
			},
		).Fatal("Unable to start as the following environment variables are not configured appropriately:")
	}
}

func getUpstreamServers() []string {
	servers := strings.Split(os.Getenv("UPSTREAM_HOSTS"), ",")

	for i := range servers {
		servers[i] = strings.TrimSpace(servers[i])
	}

	return servers
}

func createApi() {
	http.HandleFunc("/get-jobs", getJobsHandler)

	port := os.Getenv("API_PORT")
	addr := fmt.Sprintf(":%s", port)

	log.WithFields(
		log.Fields{
			"Listening Port": port,
		},
	).Info("Starting server")

	log.WithFields(
		log.Fields{
			"Servers": getUpstreamServers(),
		},
	).Info("Upstream servers:")

	err := http.ListenAndServe(addr, nil)
	if err != nil {
		log.WithFields(
			log.Fields{
				"Error": err,
			},
		).Fatal("Error starting server:")
	}
}

func main() {
	log.SetOutput(os.Stdout)

	ensureEnvironmentVariablesAreConfigured()
	createApi()
}
