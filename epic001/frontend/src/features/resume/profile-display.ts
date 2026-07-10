export function displayValue(value: string | null | undefined): string {
  return value?.trim() || "Not detected";
}

export function resumeActionLabel({
  isAnalyzing,
  isUploading,
  hasSelection,
}: {
  isAnalyzing: boolean;
  isUploading: boolean;
  hasSelection: boolean;
}): string {
  if (isAnalyzing) return "Analyzing...";
  if (isUploading) return "Loading...";
  return hasSelection ? "Upload" : "Choose File";
}
