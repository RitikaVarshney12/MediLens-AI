import { useRef, useState, type ChangeEvent, type DragEvent } from "react";

import Card from "@/components/ui/Card";
import { useUploadReport } from "@/hooks/useUploadReport";
import { useToast } from "@/hooks/useToast";
import {
  ALLOWED_EXTENSIONS,
  MAX_UPLOAD_SIZE_MB,
  validateReportFile,
} from "@/lib/reports/fileValidation";

export default function UploadDropzone() {
  const { uploadReport, isUploading, progress } = useUploadReport();
  const { showToast } = useToast();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  async function handleFile(file: File) {
    const result = validateReportFile(file);
    if (!result.valid) {
      showToast("error", result.error ?? "That file can't be uploaded.");
      return;
    }

    try {
      await uploadReport(file);
      showToast("success", `${file.name} uploaded successfully.`);
    } catch {
      showToast("error", "Upload failed. Please try again.");
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    if (file) void handleFile(file);
  }

  function handleBrowseChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) void handleFile(file);
    event.target.value = "";
  }

  return (
    <Card className="flex flex-col gap-4">
      <div>
        <h2 className="font-semibold text-ink">Upload a report</h2>
        <p className="text-sm text-ink-soft">
          PDF, JPG, or PNG. Up to {MAX_UPLOAD_SIZE_MB}MB.
        </p>
      </div>

      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`flex flex-col items-center gap-3 rounded-2xl border-2 border-dashed px-6 py-10 text-center transition-colors ${
          isDragging ? "border-primary-400 bg-primary-50" : "border-surface-border bg-surface-subtle"
        }`}
      >
        <span className="text-3xl" aria-hidden="true">
          📄
        </span>
        <p className="text-sm text-ink-soft">Drag and drop a file here, or</p>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
          className="rounded-xl bg-primary-500 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-600 disabled:cursor-not-allowed disabled:opacity-70"
        >
          Browse files
        </button>
        <input
          ref={inputRef}
          type="file"
          accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(",")}
          onChange={handleBrowseChange}
          className="sr-only"
          aria-label="Upload a medical report file"
        />
      </div>

      {isUploading && (
        <div aria-live="polite">
          <div className="h-2 w-full overflow-hidden rounded-full bg-surface-border">
            <div
              className="h-full rounded-full bg-primary-500 transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="mt-1 text-right text-xs font-medium text-ink-soft">{progress}%</p>
        </div>
      )}
    </Card>
  );
}