"use client";

import { ChangeEvent, useRef, useState } from "react";

import { uploadResume } from "./upload-resume";

type SelectedResume = {
  name: string;
  size: string;
  type: string;
};

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const SUPPORTED_EXTENSIONS = ["pdf", "doc", "docx"] as const;

export default function ResumeUploadCard() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedResume, setSelectedResume] = useState<SelectedResume | null>(
    null,
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  function openFilePicker() {
    fileInputRef.current?.click();
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const extension = getFileExtension(file.name);

    if (!isSupportedExtension(extension)) {
      setSelectedResume(null);
      setSelectedFile(null);
      setSuccessMessage(null);
      setError("Only PDF, DOC, and DOCX files are supported.");
      event.target.value = "";
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setSelectedResume(null);
      setSelectedFile(null);
      setSuccessMessage(null);
      setError("File size must be less than 10 MB.");
      event.target.value = "";
      return;
    }

    setError(null);
    setSuccessMessage(null);
    setSelectedFile(file);
    setSelectedResume({
      name: file.name,
      size: formatFileSize(file.size),
      type: extension.toUpperCase(),
    });
  }

  async function handleUpload() {
    if (!selectedFile) {
      setError("Please choose a file before uploading.");
      return;
    }

    setIsUploading(true);
    setSuccessMessage(null);
    setError(null);

    try {
      await uploadResume(selectedFile);
      setSuccessMessage("Upload Successful");
    } catch (uploadError) {
      setError(
        uploadError instanceof Error ? uploadError.message : "Upload failed",
      );
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <section className="mt-14 w-full max-w-xl rounded-lg border border-zinc-200 bg-white p-6 text-left sm:p-8">
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-zinc-950">Upload Resume</h2>
        <p className="mt-3 text-sm leading-6 text-zinc-500">
          Upload your resume to begin your AI career analysis.
        </p>
      </div>

      <button
        type="button"
        onClick={openFilePicker}
        className="mt-8 flex w-full flex-col items-center justify-center rounded-lg border border-dashed border-zinc-300 px-6 py-10 text-center transition-colors hover:bg-zinc-50"
      >
        <span className="text-3xl" aria-hidden="true">
          &#128196;
        </span>
        <span className="mt-4 text-base font-medium text-zinc-950">
          Drag &amp; Drop Resume Here
        </span>
        <span className="mt-2 text-sm text-zinc-400">or</span>
        <span className="mt-2 text-sm font-medium text-zinc-700">
          Click to Upload
        </span>
      </button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx"
        className="hidden"
        onChange={handleFileChange}
      />

      <div className="mt-5 grid gap-3 text-sm text-zinc-500 sm:grid-cols-2">
        <p>
          <span className="font-medium text-zinc-950">Supported:</span> PDF,
          DOCX, DOC
        </p>
        <p className="sm:text-right">
          <span className="font-medium text-zinc-950">Max file:</span> 10 MB
        </p>
      </div>

      <div className="mt-6 flex justify-center">
        <button
          type="button"
          onClick={openFilePicker}
          disabled={isUploading}
          className="h-11 w-56 rounded-md bg-zinc-950 px-5 text-sm font-medium text-white transition-colors hover:bg-zinc-800"
        >
          Choose File
        </button>
      </div>

      {selectedResume ? <SelectedFile resume={selectedResume} /> : null}
      {selectedFile ? (
        <div className="mt-6 flex justify-center">
          <button
            type="button"
            onClick={handleUpload}
            disabled={isUploading}
            className="h-11 w-56 rounded-md bg-zinc-950 px-5 text-sm font-medium text-white transition-colors hover:bg-zinc-800 disabled:cursor-not-allowed disabled:bg-zinc-500"
          >
            {isUploading ? "Loading..." : "Upload"}
          </button>
        </div>
      ) : null}
      {successMessage ? <UploadSuccess message={successMessage} /> : null}
      {error ? <UploadError message={error} /> : null}
    </section>
  );
}

function SelectedFile({ resume }: { resume: SelectedResume }) {
  return (
    <div className="mt-6 rounded-md border border-zinc-200 bg-zinc-50 p-4 text-sm">
      <p className="font-medium text-zinc-950">Selected File</p>
      <div className="mt-3 space-y-2 text-zinc-600">
        <p>
          <span className="font-medium text-zinc-950">Name:</span> {resume.name}
        </p>
        <p>
          <span className="font-medium text-zinc-950">Size:</span> {resume.size}
        </p>
        <p>
          <span className="font-medium text-zinc-950">Type:</span> {resume.type}
        </p>
        <p>
          <span className="font-medium text-zinc-950">Status:</span> Ready for
          upload
        </p>
      </div>
    </div>
  );
}

function UploadSuccess({ message }: { message: string }) {
  return (
    <div className="mt-6 rounded-md border border-zinc-300 bg-zinc-50 p-4 text-sm">
      <p className="font-medium text-zinc-950">{message}</p>
    </div>
  );
}

function UploadError({ message }: { message: string }) {
  return (
    <div className="mt-6 rounded-md border border-zinc-300 bg-zinc-50 p-4 text-sm">
      <p className="font-medium text-zinc-950">Error</p>
      <p className="mt-2 text-zinc-600">{message}</p>
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
