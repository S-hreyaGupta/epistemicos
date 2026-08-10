package hasher

import (
	"os"
	"path/filepath"
	"testing"
)

func TestHashBytes_Deterministic(t *testing.T) {
	h := New()
	a := h.HashBytes([]byte("hello"))
	b := h.HashBytes([]byte("hello"))
	if a != b {
		t.Errorf("expected same hash for same bytes, got %q and %q", a, b)
	}
}

func TestHashBytes_DifferentContent(t *testing.T) {
	h := New()
	if h.HashBytes([]byte("a")) == h.HashBytes([]byte("b")) {
		t.Error("expected different hashes for different content")
	}
}

func TestHashFile(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "hello.txt")
	if err := os.WriteFile(path, []byte("hello"), 0o644); err != nil {
		t.Fatalf("write file: %v", err)
	}

	h := New()
	fileHash, err := h.HashFile(path)
	if err != nil {
		t.Fatalf("HashFile: %v", err)
	}
	if fileHash != h.HashBytes([]byte("hello")) {
		t.Errorf("HashFile and HashBytes disagree: %q vs %q",
			fileHash, h.HashBytes([]byte("hello")))
	}
}
