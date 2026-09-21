// The first tests for this package.
//
// `go test ./...` reported `internal/core/services/ingest [no test files]` on
// every run from the creation of this repository until 21 September 2026. The
// store and the hasher were covered; the service that orchestrates them — the
// one that writes files, moves them, calls an external API and mutates rows —
// was not.
//
// The immediate reason for writing them is the dedupe defect: GetByHash's
// error was tested with `err == nil`, so an unreachable database during the
// lookup was read as "no duplicate exists". papers_hash_unique catches the
// consequence today, and §7.5 of the Stage 1 spec drops that constraint, so
// the repair had to land first. These controls are what stop it coming back.
//
// The stubs are deliberately dumb. Each records what it was asked and returns
// what the test told it to, so a control that passes does so because the
// service behaved, not because a fake was clever.
package ingest

import (
	"context"
	"errors"
	"io"
	"os"
	"strings"
	"testing"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
	"github.com/EpistemicOS/epistemicos/internal/core/ports"
)

// ---- stubs ----

type stubStore struct {
	byHash    *paper.Paper
	byHashErr error

	saved       []*paper.Paper
	statuses    []paper.Status
	markdownFor paper.ID
	getByID     *paper.Paper
	saveErr     error
}

func (s *stubStore) Save(_ context.Context, p *paper.Paper) error {
	if s.saveErr != nil {
		return s.saveErr
	}
	s.saved = append(s.saved, p)
	return nil
}
func (s *stubStore) GetByID(context.Context, paper.ID) (*paper.Paper, error) {
	if s.getByID != nil {
		return s.getByID, nil
	}
	return &paper.Paper{}, nil
}
func (s *stubStore) GetByHash(context.Context, paper.Hash) (*paper.Paper, error) {
	return s.byHash, s.byHashErr
}
func (s *stubStore) List(context.Context) ([]*paper.Paper, error) { return nil, nil }
func (s *stubStore) UpdateStatus(_ context.Context, _ paper.ID, st paper.Status, _ string) error {
	s.statuses = append(s.statuses, st)
	return nil
}
func (s *stubStore) UpdateMarkdown(_ context.Context, id paper.ID, _, _, _ string) error {
	s.markdownFor = id
	return nil
}

type stubHasher struct{ h paper.Hash }

func (s stubHasher) HashFile(string) (paper.Hash, error) { return s.h, nil }
func (s stubHasher) HashBytes([]byte) paper.Hash         { return s.h }

type stubProcessor struct {
	called bool
	err    error
}

func (p *stubProcessor) Process(context.Context, string) (string, string, error) {
	p.called = true
	if p.err != nil {
		return "", "", p.err
	}
	return "A Title", "# A Title\n\nSome markdown.\n", nil
}

type stubDownloader struct{}

func (stubDownloader) Download(context.Context, string) (io.ReadCloser, error) {
	return io.NopCloser(strings.NewReader("%PDF-fake")), nil
}

func newService(t *testing.T, store ports.PaperStore, proc ports.MarkdownProcessor) (*Service, string) {
	t.Helper()
	dir := t.TempDir()
	return New(store, stubDownloader{}, proc, stubHasher{h: paper.Hash("deadbeef")}, dir), dir
}

func pdf() io.Reader { return strings.NewReader("%PDF-fake") }

// ---- the dedupe decision ----

// The control this package was written for. A database that cannot answer is
// not a database saying no.
func TestDedupeLookupFailureStopsIngest(t *testing.T) {
	boom := errors.New("connection refused")
	store := &stubStore{byHashErr: boom}
	proc := &stubProcessor{}
	svc, _ := newService(t, store, proc)

	_, err := svc.FromUpload(context.Background(), pdf())

	if err == nil {
		t.Fatal("ingest continued after the dedupe lookup failed. An " +
			"unreachable database would be read as 'no duplicate exists', " +
			"and a paper already held would be stored a second time.")
	}
	if !errors.Is(err, boom) {
		t.Fatalf("the underlying failure was not preserved: %v", err)
	}
	if len(store.saved) != 0 {
		t.Fatalf("a row was written despite the lookup failing: %d saved",
			len(store.saved))
	}
	if proc.called {
		t.Fatal("the markdown processor was called despite the lookup failing")
	}
}

// The other side of the same branch, so the control above cannot pass by the
// service refusing everything.
func TestNotFoundMeansProceed(t *testing.T) {
	store := &stubStore{byHashErr: ports.ErrNotFound}
	proc := &stubProcessor{}
	svc, _ := newService(t, store, proc)

	if _, err := svc.FromUpload(context.Background(), pdf()); err != nil {
		t.Fatalf("a genuinely new paper was refused: %v", err)
	}
	if len(store.saved) != 1 {
		t.Fatalf("expected one row written, got %d", len(store.saved))
	}
	if !proc.called {
		t.Fatal("the markdown processor was never called for a new paper")
	}
}

// And the hit, which must not reach the processor at all.
func TestExistingPaperIsReturnedWithoutReprocessing(t *testing.T) {
	want := &paper.Paper{ID: paper.ID("already-here"), Hash: paper.Hash("deadbeef")}
	store := &stubStore{byHash: want}
	proc := &stubProcessor{}
	svc, dir := newService(t, store, proc)

	got, err := svc.FromUpload(context.Background(), pdf())
	if err != nil {
		t.Fatalf("a duplicate was not returned: %v", err)
	}
	if got.ID != want.ID {
		t.Fatalf("returned %q, want the existing %q", got.ID, want.ID)
	}
	if proc.called {
		t.Fatal("a duplicate went through the markdown processor; that is a " +
			"paid external call for a document already held")
	}
	if len(store.saved) != 0 {
		t.Fatalf("a duplicate created %d new row(s)", len(store.saved))
	}
	// And the staged file is not left behind.
	entries, _ := os.ReadDir(dir)
	for _, e := range entries {
		if strings.HasPrefix(e.Name(), "tmp-") {
			t.Fatalf("the temp file survived a dedupe hit: %s", e.Name())
		}
	}
}

// ---- the temp file, on each path ----

// Every early return has to clean up after itself, or a failing ingest leaves
// PDFs in the staging directory until something fills.
func TestTempFileIsRemovedWhenTheLookupFails(t *testing.T) {
	store := &stubStore{byHashErr: errors.New("connection refused")}
	svc, dir := newService(t, store, &stubProcessor{})

	_, _ = svc.FromUpload(context.Background(), pdf())

	entries, err := os.ReadDir(dir)
	if err != nil {
		t.Fatalf("read staging dir: %v", err)
	}
	for _, e := range entries {
		if strings.HasPrefix(e.Name(), "tmp-") {
			t.Fatalf("a staged file was left behind after a failed lookup: %s",
				e.Name())
		}
	}
}

// ---- entry points ----

func TestFromURLRequiresAURL(t *testing.T) {
	svc, _ := newService(t, &stubStore{byHashErr: ports.ErrNotFound}, &stubProcessor{})
	if _, err := svc.FromURL(context.Background(), ""); err == nil {
		t.Fatal("an empty URL was accepted")
	}
}

// A conversion failure must mark the row rather than leaving it pending, or a
// paper sits in the database claiming to be mid-flight forever.
func TestProcessorFailureMarksThePaperFailed(t *testing.T) {
	store := &stubStore{byHashErr: ports.ErrNotFound}
	proc := &stubProcessor{err: errors.New("mathpix exploded")}
	svc, _ := newService(t, store, proc)

	if _, err := svc.FromUpload(context.Background(), pdf()); err == nil {
		t.Fatal("a conversion failure was reported as success")
	}
	var sawFailed bool
	for _, st := range store.statuses {
		if st == paper.StatusFailed {
			sawFailed = true
		}
	}
	if !sawFailed {
		t.Fatalf("the paper was never marked failed; statuses recorded: %v",
			store.statuses)
	}
}
