// Package hasher implements content-addressed hashing for paper dedupe.
//
// It implements ports.Hasher and produces a paper.Hash. MD5 is adequate
// here: the hash is a dedupe key, not a security boundary.
package hasher

import (
	"crypto/md5"
	"fmt"
	"io"
	"os"

	"github.com/EpistemicOS/epistemicos/internal/core/domain/paper"
)

// MD5Hasher hashes file contents with MD5. MD5 is fine for content
// addressing — it's not used for security.
type MD5Hasher struct{}

// New returns a ready-to-use MD5Hasher.
func New() MD5Hasher { return MD5Hasher{} }

// HashFile reads the file at filePath and returns its MD5 hex digest.
func (MD5Hasher) HashFile(filePath string) (paper.Hash, error) {
	f, err := os.Open(filePath)
	if err != nil {
		return "", fmt.Errorf("open %s: %w", filePath, err)
	}
	defer f.Close()

	h := md5.New()
	if _, err := io.Copy(h, f); err != nil {
		return "", fmt.Errorf("read %s: %w", filePath, err)
	}
	return paper.Hash(fmt.Sprintf("%x", h.Sum(nil))), nil
}

// HashBytes returns the MD5 hex digest of the given content.
func (MD5Hasher) HashBytes(content []byte) paper.Hash {
	sum := md5.Sum(content)
	return paper.Hash(fmt.Sprintf("%x", sum))
}
