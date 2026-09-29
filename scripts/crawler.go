package main

import (
	"encoding/json"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strings"
	"time"
)

type Intent struct {
	ID       string   `json:"id"`
	Template string   `json:"template"`
	Terms    []string `json:"terms"`
	Limit    int      `json:"limit"`
}

type Template struct {
	Engine    string   `json:"engine"`
	Intents   []Intent `json:"intents"`
	UserAgent string   `json:"user_agent"`
}

type RSS struct {
	Channel struct {
		Items []struct {
			Title   string `xml:"title"`
			Link    string `xml:"link"`
			PubDate string `xml:"pubDate"`
			Source  string `xml:"source"`
			Desc    string `xml:"description"`
		} `xml:"item"`
	} `xml:"channel"`
}

type Observation struct {
	ObservedAt  string `json:"observed_at"`
	Kind        string `json:"kind"`
	Intent      string `json:"intent"`
	Query       string `json:"query"`
	Title       string `json:"title"`
	URL         string `json:"url"`
	PublishedAt string `json:"published_at,omitempty"`
	Source      string `json:"source,omitempty"`
	Description string `json:"description,omitempty"`
	Discovery   string `json:"discovery_engine"`
}

func main() {
	templatePath := getenv("CRAWL_TEMPLATE", "aw/crawler-template.json")
	outPath := getenv("CRAWL_OUTPUT", "data/observations.jsonl")
	t, err := loadTemplate(templatePath)
	if err != nil { fatal(err) }

	ua := t.UserAgent
	if ua == "" { ua = "bonsai/idol-db-crawler/1.0" }

	client := &http.Client{Timeout: 20 * time.Second}
	seen := map[string]bool{}
	var observations []Observation

	for _, intent := range t.Intents {
		terms := intent.Terms
		if len(terms) == 0 { terms = []string{""} }
		limit := intent.Limit
		if limit <= 0 { limit = 10 }

		for _, term := range terms {
			q := strings.TrimSpace(fmt.Sprintf(intent.Template, term))
			if q == "" { continue }

			for _, engine := range engines(t.Engine) {
				items, err := searchRSS(client, engine, q, ua)
				if err != nil {
					fmt.Fprintf(os.Stderr, "intent=%s engine=%s query=%q: %v\n", intent.ID, engine, q, err)
					continue
				}
				n := 0
				for _, item := range items {
					if n >= limit { break }
					u := strings.TrimSpace(item.Link)
					if u == "" || seen[u] { continue }
					seen[u] = true
					observations = append(observations, Observation{
						ObservedAt: time.Now().UTC().Format(time.RFC3339),
						Kind: "search_result",
						Intent: intent.ID,
						Query: q,
						Title: strings.TrimSpace(item.Title),
						URL: u,
						PublishedAt: strings.TrimSpace(item.PubDate),
						Source: strings.TrimSpace(item.Source),
						Description: stripHTML(item.Desc),
						Discovery: engine,
					})
					n++
				}
			}
		}
	}

	if err := appendJSONL(outPath, observations); err != nil { fatal(err) }
	fmt.Printf("crawler: %d new observations -> %s\n", len(observations), outPath)
}

func loadTemplate(path string) (Template, error) {
	b, err := os.ReadFile(path)
	if err != nil { return Template{}, err }
	var t Template
	if err := json.Unmarshal(b, &t); err != nil { return Template{}, err }
	return t, nil
}

func engines(name string) []string {
	switch strings.ToLower(strings.TrimSpace(name)) {
	case "bing": return []string{"bing"}
	case "google-news": return []string{"google-news"}
	default: return []string{"bing", "google-news"}
	}
}

type Item struct {
	Title, Link, PubDate, Source, Desc string
}

func searchRSS(client *http.Client, engine, q, ua string) ([]Item, error) {
	var endpoint string
	switch engine {
	case "bing":
		endpoint = "https://www.bing.com/search?format=rss&q=" + url.QueryEscape(q)
	case "google-news":
		endpoint = "https://news.google.com/rss/search?q=" + url.QueryEscape(q) + "&hl=ja&gl=JP&ceid=JP:ja"
	default:
		return nil, fmt.Errorf("unknown engine: %s", engine)
	}

	req, err := http.NewRequest(http.MethodGet, endpoint, nil)
	if err != nil { return nil, err }
	req.Header.Set("User-Agent", ua)
	req.Header.Set("Accept", "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8")

	resp, err := client.Do(req)
	if err != nil { return nil, err }
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK { return nil, fmt.Errorf("HTTP %s", resp.Status) }

	body, err := io.ReadAll(io.LimitReader(resp.Body, 5<<20))
	if err != nil { return nil, err }

	var rss RSS
	if err := xml.Unmarshal(body, &rss); err != nil { return nil, err }

	out := make([]Item, 0, len(rss.Channel.Items))
	for _, item := range rss.Channel.Items {
		out = append(out, Item{item.Title, item.Link, item.PubDate, item.Source, item.Desc})
	}
	return out, nil
}

func appendJSONL(path string, rows []Observation) error {
	if len(rows) == 0 { return nil }
	if err := os.MkdirAll("data", 0o755); err != nil { return err }
	f, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil { return err }
	defer f.Close()
	enc := json.NewEncoder(f)
	for _, row := range rows {
		if err := enc.Encode(row); err != nil { return err }
	}
	return nil
}

func stripHTML(s string) string {
	var b strings.Builder
	inTag := false
	for _, r := range s {
		switch r {
		case '<': inTag = true
		case '>': inTag = false
		default:
			if !inTag { b.WriteRune(r) }
		}
	}
	return strings.Join(strings.Fields(b.String()), " ")
}

func getenv(key, fallback string) string {
	if v := os.Getenv(key); v != "" { return v }
	return fallback
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, err)
	os.Exit(1)
}
