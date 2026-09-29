package main

import (
  "crypto/sha256"
  "encoding/hex"
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
  ID string `json:"id"`
  Family string `json:"family"`
  Purpose string `json:"purpose"`
  Template string `json:"template"`
  Terms []string `json:"terms"`
  Limit int `json:"limit"`
  Enabled bool `json:"enabled"`
}
type Template struct {
  Version string `json:"version"`
  Contract string `json:"contract"`
  Engine string `json:"engine"`
  Intents []Intent `json:"intents"`
  UserAgent string `json:"user_agent"`
  MaxQueries int `json:"max_queries"`
  TimeoutSeconds int `json:"timeout_seconds"`
  DedupeKey string `json:"dedupe_key"`
}
type RSS struct {
  Channel struct {
    Items []struct {
      Title string `xml:"title"`
      Link string `xml:"link"`
      PubDate string `xml:"pubDate"`
      Source string `xml:"source"`
      Desc string `xml:"description"`
    } `xml:"item"`
  } `xml:"channel"`
}
type Observation struct {
  ObservationID string `json:"observation_id"`
  ObservedAt string `json:"observed_at"`
  Family string `json:"family"`
  Intent string `json:"intent"`
  Kind string `json:"kind"`
  Query string `json:"query"`
  Title string `json:"title"`
  URL string `json:"url"`
  PublishedAt string `json:"published_at,omitempty"`
  SourceName string `json:"source_name,omitempty"`
  SourceKind string `json:"source_kind"`
  Description string `json:"description,omitempty"`
  Discovery string `json:"discovery_engine"`
  SubjectType string `json:"subject_type"`
}

func main() {
  templatePath := getenv("CRAWL_TEMPLATE", "aw/crawler-template.json")
  outPath := getenv("CRAWL_OUTPUT", "data/observations.jsonl")
  t, err := loadTemplate(templatePath); if err != nil { fatal(err) }
  ua := t.UserAgent; if ua == "" { ua = "bonsai/idol-db-crawler/1.0" }
  timeout := time.Duration(t.TimeoutSeconds) * time.Second
  if timeout <= 0 { timeout = 20 * time.Second }
  client := &http.Client{Timeout: timeout}
  seen := map[string]bool{}
  var observations []Observation
  queries := 0
  maxQueries := t.MaxQueries; if maxQueries <= 0 { maxQueries = 500 }

  for _, intent := range t.Intents {
    if !intent.Enabled { continue }
    terms := intent.Terms; if len(terms) == 0 { terms = []string{""} }
    limit := intent.Limit; if limit <= 0 { limit = 10 }
    for _, term := range terms {
      if queries >= maxQueries { break }
      q := strings.TrimSpace(fmt.Sprintf(intent.Template, term)); if q == "" { continue }
      queries++
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
          observed := time.Now().UTC()
          observations = append(observations, Observation{
            ObservationID: observationID(intent.ID, u, observed),
            ObservedAt: observed.Format(time.RFC3339),
            Family: intent.Family,
            Intent: intent.ID,
            Kind: kindFor(intent.Family),
            Query: q,
            Title: strings.TrimSpace(item.Title),
            URL: u,
            PublishedAt: strings.TrimSpace(item.PubDate),
            SourceName: strings.TrimSpace(item.Source),
            SourceKind: sourceKind(engine),
            Description: stripHTML(item.Desc),
            Discovery: engine,
            SubjectType: subjectType(intent.Family),
          })
          n++
        }
      }
    }
    if queries >= maxQueries { break }
  }
  if err := appendJSONL(outPath, observations); err != nil { fatal(err) }
  fmt.Printf("crawler: %d queries, %d new observations -> %s\n", queries, len(observations), outPath)
}

func loadTemplate(path string) (Template, error) {
  b, err := os.ReadFile(path); if err != nil { return Template{}, err }
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
type Item struct{ Title, Link, PubDate, Source, Desc string }
func searchRSS(client *http.Client, engine, q, ua string) ([]Item, error) {
  var endpoint string
  switch engine {
  case "bing": endpoint = "https://www.bing.com/search?format=rss&q=" + url.QueryEscape(q)
  case "google-news": endpoint = "https://news.google.com/rss/search?q=" + url.QueryEscape(q) + "&hl=ja&gl=JP&ceid=JP:ja"
  default: return nil, fmt.Errorf("unknown engine: %s", engine)
  }
  req, err := http.NewRequest(http.MethodGet, endpoint, nil); if err != nil { return nil, err }
  req.Header.Set("User-Agent", ua)
  req.Header.Set("Accept", "application/rss+xml, application/xml;q=0.9, text/xml;q=0.8")
  resp, err := client.Do(req); if err != nil { return nil, err }
  defer resp.Body.Close()
  if resp.StatusCode != http.StatusOK { return nil, fmt.Errorf("HTTP %s", resp.Status) }
  body, err := io.ReadAll(io.LimitReader(resp.Body, 5<<20)); if err != nil { return nil, err }
  var rss RSS
  if err := xml.Unmarshal(body, &rss); err != nil { return nil, err }
  out := make([]Item, 0, len(rss.Channel.Items))
  for _, item := range rss.Channel.Items { out = append(out, Item{item.Title, item.Link, item.PubDate, item.Source, item.Desc}) }
  return out, nil
}
func appendJSONL(path string, rows []Observation) error {
  if len(rows) == 0 { return nil }
  if err := os.MkdirAll("data", 0o755); err != nil { return err }
  f, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644); if err != nil { return err }
  defer f.Close()
  enc := json.NewEncoder(f)
  for _, row := range rows { if err := enc.Encode(row); err != nil { return err } }
  return nil
}
func observationID(intent, u string, t time.Time) string {
  sum := sha256.Sum256([]byte(intent + "|" + u + "|" + t.Format(time.RFC3339Nano)))
  return "obs_" + hex.EncodeToString(sum[:8])
}
func kindFor(family string) string {
  switch family {
  case "music": return "track_signal"
  case "business": return "business_signal"
  case "fan": return "mention"
  default: return "search_result"
  }
}
func sourceKind(engine string) string {
  if engine == "google-news" { return "news" }
  return "web"
}
func subjectType(family string) string {
  switch family {
  case "music": return "song"
  case "event": return "event"
  default: return "unknown"
  }
}
func stripHTML(s string) string {
  var b strings.Builder; inTag := false
  for _, r := range s {
    switch r { case '<': inTag = true; case '>': inTag = false; default: if !inTag { b.WriteRune(r) } }
  }
  return strings.Join(strings.Fields(b.String()), " ")
}
func getenv(key, fallback string) string { if v := os.Getenv(key); v != "" { return v }; return fallback }
func fatal(err error) { fmt.Fprintln(os.Stderr, err); os.Exit(1) }
