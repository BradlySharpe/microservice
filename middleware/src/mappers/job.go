package mappers

type Job struct {
	Source      string   `json:"source"`
	Id          string   `json:"id"`
	Url         string   `json:"url"`
	CompanyName string   `json:"company_name"`
	CompanyLogo string   `json:"company_logo"`
	Title       string   `json:"title"`
	Description string   `json:"description"`
	Type        string   `json:"type"`
	Category    string   `json:"category"`
	Published   string   `json:"published"`
	Expires     string   `json:"expires"`
	Locations   []string `json:"locations"`
	Salary      string   `json:"salary"`
	Tags        []string `json:"tags"`
	Skills      []string `json:"skills"`
}
