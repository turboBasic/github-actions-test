package probe

import "github.com/google/uuid"

// Named for the same thing src/probe answers: what this repository is a consumer of.
func Describe() string {
	return "consumer of turboBasic/github-actions"
}

// The external dependency exists so `deps` has a module graph to download and verify, and so the
// build stage compiles against something the lockfile-equivalent pins.
func RunID() string {
	return uuid.NewSHA1(uuid.NameSpaceURL, []byte(Describe())).String()
}
