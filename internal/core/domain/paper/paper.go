// Package paper defines the Paper aggregate.
//
// A Paper is the unit of analysis. It carries its source markdown
// (produced upstream by Mathpix), a content hash of the source PDF for
// dedupe, and a separate hash of the markdown itself for integrity.
//
// A Span/Document/Section trio used to live alongside this type, describing a
// paper's sections for the extractor pipeline. Both were removed: nothing here
// consumes them, and their CharStart/CharEnd fields held byte values under
// character names. Anything downstream that sections a paper should index the
// markdown by byte offset and verify those offsets against MarkdownHash.
package paper

import "time"

// ID is the persistent identifier for a paper. UUID string.
type ID string

// Hash is the content-addressed identifier for the source PDF.
// Two papers with the same Hash are the same paper.
type Hash string

// Status tracks the ingestion lifecycle.
type Status string

const (
	StatusPending     Status = "pending"     // accepted, not yet downloaded
	StatusDownloading Status = "downloading" // PDF being fetched
	StatusProcessing  Status = "processing"  // Mathpix converting to markdown
	StatusReady       Status = "ready"       // markdown + hash stored
	StatusFailed      Status = "failed"      // ingestion failed; see Error
)

// Paper is the persisted record. Markdown is populated once Mathpix completes.
type Paper struct {
	ID     ID
	URL    string // upstream source URL (may be empty for direct uploads)
	Hash   Hash
	Title  string
	Status Status
	Error  string // populated when Status == StatusFailed

	Markdown     string // produced by Mathpix; the upstream contract is markdown-with-LaTeX
	MarkdownHash string // hex-encoded SHA-256 of Markdown, written alongside it

	CreatedAt time.Time
	UpdatedAt time.Time
}
