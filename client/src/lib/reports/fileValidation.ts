export const ALLOWED_EXTENSIONS = ["pdf", "jpg", "jpeg", "png"] as const;

export const ALLOWED_MIME_TYPES = [
  "application/pdf",
  "image/jpeg",
  "image/jpg",
  "image/png",
] as const;

export const MAX_UPLOAD_SIZE_MB = 20;
export const MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024;

export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

export function validateReportFile(file: File): FileValidationResult {
  const extension = file.name.split(".").pop()?.toLowerCase() ?? "";

  if (!ALLOWED_EXTENSIONS.includes(extension as (typeof ALLOWED_EXTENSIONS)[number])) {
    return { valid: false, error: "Unsupported file type. Allowed: PDF, JPG, JPEG, PNG." };
  }

  if (!ALLOWED_MIME_TYPES.includes(file.type as (typeof ALLOWED_MIME_TYPES)[number])) {
    return { valid: false, error: "Unsupported file content type." };
  }

  if (file.size === 0) {
    return { valid: false, error: "File is empty." };
  }

  if (file.size > MAX_UPLOAD_SIZE_BYTES) {
    return { valid: false, error: `File exceeds the ${MAX_UPLOAD_SIZE_MB}MB limit.` };
  }

  return { valid: true };
}