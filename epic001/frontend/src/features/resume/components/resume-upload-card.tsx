"use client";

import { ChangeEvent, FormEvent, useRef, useState } from "react";

import { uploadResume } from "../api/upload-resume";
import { parseResume } from "../api/parse-resume";
import type { ResumeProfile as ResumeProfileData, SelectedResume } from "../types";
import { ResumeFilePicker } from "./resume-file-picker";
import { ResumeProfile } from "./resume-profile";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const SUPPORTED_EXTENSIONS = ["pdf", "doc", "docx"] as const;

export function ResumeUploadCard() {
  const lastHandledFile = useRef<File | null>(null);
  const [selectedResume, setSelectedResume] = useState<SelectedResume | null>(
    null,
  );
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [profile, setProfile] = useState<ResumeProfileData | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement> | FormEvent<HTMLInputElement>,
  ) {
    const file = event.currentTarget.files?.[0];
    if (!file) return;
    if (lastHandledFile.current === file) return;
    selectAndAnalyze(file, event.currentTarget);
  }

  function selectAndAnalyze(file: File, input?: HTMLInputElement) {
    const extension = getFileExtension(file.name);
    if (!isSupportedExtension(extension)) {
      lastHandledFile.current = null;
      resetSelection("Only PDF, DOC, and DOCX files are supported.");
      if (input) input.value = "";
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      lastHandledFile.current = null;
      resetSelection("File size must be less than 10 MB.");
      if (input) input.value = "";
      return;
    }

    lastHandledFile.current = file;
    setError(null);
    setSuccessMessage(null);
    setProfile(null);
    setSelectedResume({
      name: file.name,
      size: formatFileSize(file.size),
      type: extension.toUpperCase(),
    });
    void analyzeFile(file);
  }

  function handleAnalyze(file: File | null) {
    if (!file) {
      setError("Please choose a file before analyzing.");
      return;
    }
    if (lastHandledFile.current === file) {
      void analyzeFile(file);
      return;
    }
    selectAndAnalyze(file);
  }

  function resetSelection(message: string) {
    setSelectedResume(null);
    setSuccessMessage(null);
    setProfile(null);
    setError(message);
  }

  async function analyzeFile(file: File) {
    setIsUploading(true);
    setSuccessMessage(null);
    setError(null);

    try {
      const extension = getFileExtension(file.name);
      if (extension === "pdf") {
        setIsAnalyzing(true);
        const result = await parseResume(file);
        setProfile(result.profile);
        setSuccessMessage("Resume analysis complete");
      } else {
        await uploadResume(file);
        setSuccessMessage("Upload Successful");
      }
    } catch (uploadError) {
      setError(
        uploadError instanceof Error ? uploadError.message : "Upload failed",
      );
    } finally {
      setIsAnalyzing(false);
      setIsUploading(false);
    }
  }

  return (
    <section className="upload-card">
      <div className="upload-card__heading">
        <h2>Upload Resume</h2>
        <p>Upload your resume to begin your AI career analysis.</p>
      </div>
      <ResumeFilePicker
        buttonLabel="Choose File"
        disabled={isUploading}
        onChange={handleFileChange}
        onAnalyze={handleAnalyze}
        analyzeLabel={
          isAnalyzing ? "Analyzing..." : isUploading ? "Loading..." : "Analyze Resume"
        }
      />
      <div className="file-rules">
        <p>
          <strong>Supported:</strong> PDF, DOCX, DOC
        </p>
        <p>
          <strong>Max file:</strong> 10 MB
        </p>
      </div>
      {selectedResume ? <SelectedFile resume={selectedResume} /> : null}
      {successMessage ? <StatusMessage message={successMessage} /> : null}
      {error ? <StatusMessage title="Error" message={error} /> : null}
      {profile ? <ResumeProfile profile={profile} /> : null}
    </section>
  );
}

function SelectedFile({ resume }: { resume: SelectedResume }) {
  return (
    <div className="status-panel">
      <strong>Selected File</strong>
      <p>Name: {resume.name}</p>
      <p>Size: {resume.size}</p>
      <p>Type: {resume.type}</p>
      <p>Status: Ready for upload</p>
    </div>
  );
}

function StatusMessage({
  title,
  message,
}: {
  title?: string;
  message: string;
}) {
  return (
    <div className="status-panel" role="status">
      {title ? <strong>{title}</strong> : null}
      <p>{message}</p>
    </div>
  );
}

function getFileExtension(fileName: string) {
  return fileName.split(".").pop()?.toLowerCase() ?? "";
}

function isSupportedExtension(
  extension: string,
): extension is (typeof SUPPORTED_EXTENSIONS)[number] {
  return SUPPORTED_EXTENSIONS.some((supported) => supported === extension);
}

function formatFileSize(size: number) {
  return `${(size / 1024 / 1024).toFixed(2)} MB`;
}
