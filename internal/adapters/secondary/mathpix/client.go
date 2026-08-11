// Package mathpix implements ports.MarkdownProcessor against the
// Mathpix v3 PDF-to-markdown API.
//
// Mathpix is the production input contract: PDFs in, markdown-with-LaTeX
// out. This system does not re-OCR — fidelity at this layer is
// upstream's responsibility.
package mathpix

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"strings"
	"time"
)

const defaultBaseURL = "https://api.mathpix.com/v3"

// Client implements ports.MarkdownProcessor.
type Client struct {
	appID   string
	appKey  string
	baseURL string
	client  *http.Client
}

// New returns a Mathpix client. Both appID and appKey are required.
func New(appID, appKey string) *Client {
	return &Client{
		appID:   appID,
		appKey:  appKey,
		baseURL: defaultBaseURL,
		client:  http.DefaultClient,
	}
}

// WithHTTPClient lets callers swap the HTTP client (timeouts, transports).
func (c *Client) WithHTTPClient(h *http.Client) *Client {
	if h != nil {
		c.client = h
	}
	return c
}

// WithBaseURL is used by tests to point at a stubbed server.
func (c *Client) WithBaseURL(u string) *Client {
	c.baseURL = u
	return c
}

type pdfResponse struct {
	PDFID string `json:"pdf_id"`
}

type statusResponse struct {
	Status       string  `json:"status"`
	PercentDone  float64 `json:"percent_done"`
	ErrorMessage string  `json:"error,omitempty"`
}

// Process uploads the PDF at filePath, polls until conversion completes,
// and returns the inferred title + markdown body.
func (c *Client) Process(ctx context.Context, filePath string) (string, string, error) {
	pdfID, err := c.upload(ctx, filePath)
	if err != nil {
		return "", "", fmt.Errorf("upload: %w", err)
	}

	if err := c.waitForCompletion(ctx, pdfID); err != nil {
		return "", "", fmt.Errorf("processing: %w", err)
	}

	title, markdown, err := c.getResult(ctx, pdfID)
	if err != nil {
		return "", "", fmt.Errorf("get result: %w", err)
	}

	return title, markdown, nil
}

func (c *Client) upload(ctx context.Context, filePath string) (string, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	var body bytes.Buffer
	writer := multipart.NewWriter(&body)

	part, err := writer.CreateFormFile("file", filePath)
	if err != nil {
		return "", err
	}
	if _, err := io.Copy(part, f); err != nil {
		return "", err
	}
	if err := writer.WriteField("options_json", `{"conversion_formats":{"md":true}}`); err != nil {
		return "", err
	}
	writer.Close()

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/pdf", &body)
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", writer.FormDataContentType())
	c.setAuthHeaders(req)

	resp, err := c.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		b, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("upload failed with status %d: %s", resp.StatusCode, b)
	}

	b, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	var result pdfResponse
	if err := json.Unmarshal(b, &result); err != nil {
		return "", fmt.Errorf("decode upload response: %s", b)
	}
	if result.PDFID == "" {
		return "", fmt.Errorf("empty pdf_id in response: %s", b)
	}
	return result.PDFID, nil
}

func (c *Client) waitForCompletion(ctx context.Context, pdfID string) error {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			status, err := c.getStatus(ctx, pdfID)
			if err != nil {
				return err
			}
			switch status.Status {
			case "completed":
				return nil
			case "error":
				return fmt.Errorf("mathpix error: %s", status.ErrorMessage)
			}
		}
	}
}

func (c *Client) getStatus(ctx context.Context, pdfID string) (*statusResponse, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+"/pdf/"+pdfID, nil)
	if err != nil {
		return nil, err
	}
	c.setAuthHeaders(req)

	resp, err := c.client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		b, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("status check failed with status %d: %s", resp.StatusCode, b)
	}

	var status statusResponse
	if err := json.NewDecoder(resp.Body).Decode(&status); err != nil {
		return nil, err
	}
	return &status, nil
}

func (c *Client) getResult(ctx context.Context, pdfID string) (string, string, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, c.baseURL+"/pdf/"+pdfID+".md", nil)
	if err != nil {
		return "", "", err
	}
	c.setAuthHeaders(req)

	resp, err := c.client.Do(req)
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", "", err
	}
	if resp.StatusCode != http.StatusOK {
		return "", "", fmt.Errorf("get result failed with status %d: %s", resp.StatusCode, body)
	}

	title := extractTitle(string(body))
	return title, string(body), nil
}

func extractTitle(markdown string) string {
	for _, line := range strings.SplitN(markdown, "\n", 10) {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "# ") {
			return strings.TrimPrefix(line, "# ")
		}
	}
	return ""
}

func (c *Client) setAuthHeaders(req *http.Request) {
	req.Header.Set("app_id", c.appID)
	req.Header.Set("app_key", c.appKey)
}
