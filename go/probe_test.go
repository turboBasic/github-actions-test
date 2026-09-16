package probe

import "testing"

func TestDescribeNamesTheUpstream(t *testing.T) {
	if got := Describe(); got != "consumer of turboBasic/github-actions" {
		t.Errorf("Describe() = %q", got)
	}
}

func TestRunIDIsDerivedFromTheDescriptionAndStable(t *testing.T) {
	if RunID() != RunID() {
		t.Error("RunID() is not stable, so the dependency is not doing what this asserts")
	}
	if len(RunID()) != 36 {
		t.Errorf("RunID() = %q, want a 36-character UUID", RunID())
	}
}
