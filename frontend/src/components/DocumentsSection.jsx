import { useState, useEffect, useCallback } from "react";
import {
  listDocuments,
  uploadDocument,
  resubmitApplication,
  ApiError,
} from "../services/api";

const DOCUMENT_TYPE_OPTIONS = [
  { label: "Payslip", value: "PAYSLIP" },
  { label: "Bank Statement", value: "BANK_STATEMENT" },
  { label: "Tax Return", value: "TAX_RETURN" },
];

const ALLOWED_MIME_TYPES = ["application/pdf", "image/png", "image/jpeg"];
const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

function documentTypeLabel(value) {
  const match = DOCUMENT_TYPE_OPTIONS.find((o) => o.value === value);
  return match ? match.label : value;
}

function formatFileSize(bytes) {
  if (!Number.isFinite(bytes)) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function validateFile(file) {
  if (!ALLOWED_MIME_TYPES.includes(file.type)) {
    return "Only PDF, PNG or JPEG files are supported.";
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return "File must be 5 MB or smaller.";
  }
  return null;
}

export default function DocumentsSection({
  applicationId,
  onSessionExpired,
  canUpload = false,
  onResubmitted,
}) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [listError, setListError] = useState(null);
  const [documentType, setDocumentType] = useState("PAYSLIP");
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [isResubmitting, setIsResubmitting] = useState(false);
  const [resubmitMessage, setResubmitMessage] = useState(null);
  const [documentReplaced, setDocumentReplaced] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  const loadDocuments = useCallback(async () => {
    setIsLoading(true);
    setListError(null);

    try {
      const result = await listDocuments(applicationId);
      setDocuments(result);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }

      setListError(
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred while loading documents."
      );
    } finally {
      setIsLoading(false);
    }
  }, [applicationId, onSessionExpired]);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  function handleFileChosen(file) {
    setUploadError(null);
    setResubmitMessage(null);

    if (!file) {
      setSelectedFile(null);
      setFileError(null);
      return;
    }

    const validationError = validateFile(file);
    setFileError(validationError);
    setSelectedFile(validationError ? null : file);
  }

  async function handleUpload() {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadError(null);
    setResubmitMessage(null);

    try {
      const newDocument = await uploadDocument(
        applicationId,
        documentType,
        selectedFile
      );
      setDocuments((prev) => [newDocument, ...prev]);
      setSelectedFile(null);
      setFileError(null);
      setDocumentReplaced(true);
      setResubmitMessage(
        `${documentTypeLabel(documentType)} replaced successfully. Submit the updated application for advisor review.`
      );
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }

      setUploadError(
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred while uploading."
      );
    } finally {
      setIsUploading(false);
    }
  }

  async function handleResubmit() {
    setIsResubmitting(true);
    setResubmitMessage(null);
    setUploadError(null);

    try {
      await resubmitApplication(applicationId);
      setDocumentReplaced(false);
      setResubmitMessage(
        "Application resubmitted successfully. It is now back in the advisor review queue."
      );
      onResubmitted?.();
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }

      setResubmitMessage(
        error instanceof ApiError
          ? error.message
          : "The application could not be resubmitted."
      );
    } finally {
      setIsResubmitting(false);
    }
  }

  const hasCurrentReplacement = documentReplaced;

  return (
    <div className="documents-section">
      <h3 className="detail-section-heading">
        {canUpload ? "Application Documents" : "Submitted Documents"}
      </h3>
      <p className="documents-intro">
        {canUpload
          ? "Replace a document to provide updated information. The previous version is kept in history."
          : "Documents submitted with this application."}
      </p>

      {canUpload && (
        <>
          <div
            className={`upload-dropzone ${isDragOver ? "upload-dropzone-active" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(event) => {
              event.preventDefault();
              setIsDragOver(false);
              handleFileChosen(event.dataTransfer.files?.[0] || null);
            }}
          >
            <p className="upload-dropzone-title">
              {selectedFile
                ? selectedFile.name
                : "Upload a replacement document"}
            </p>
            <p className="upload-dropzone-hint">
              {selectedFile
                ? formatFileSize(selectedFile.size)
                : "PDF, PNG or JPEG · Maximum 5 MB"}
            </p>
            <label className="upload-choose-button">
              {selectedFile ? "Change Document" : "Choose Document"}
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
                onChange={(event) =>
                  handleFileChosen(event.target.files?.[0] || null)
                }
                hidden
              />
            </label>
          </div>

          {fileError && (
            <p className="field-error" role="alert">
              {fileError}
            </p>
          )}

          <div className="upload-controls-row">
            <div className="form-field upload-type-field">
              <label htmlFor="replacement_document_type">Document type</label>
              <select
                id="replacement_document_type"
                value={documentType}
                onChange={(event) => {
                  setDocumentType(event.target.value);
                  setUploadError(null);
                  setResubmitMessage(null);
                }}
              >
                {DOCUMENT_TYPE_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              className="submit-button upload-submit-button"
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? "Uploading…" : "Replace Document"}
            </button>
          </div>

          {uploadError && (
            <div className="submit-error" role="alert">
              {uploadError}
            </div>
          )}

          {resubmitMessage && (
            <div className="documents-action-message" role="status">
              {resubmitMessage}
            </div>
          )}

          {hasCurrentReplacement && (
            <button
              type="button"
              className="submit-button resubmit-button"
              onClick={handleResubmit}
              disabled={isResubmitting}
            >
              {isResubmitting
                ? "Resubmitting…"
                : "Resubmit for Advisor Review"}
            </button>
          )}
        </>
      )}

      <div className="document-list">
        {isLoading && (
          <p className="dashboard-status-text">Loading documents…</p>
        )}

        {!isLoading && listError && (
          <div className="submit-error" role="alert">
            {listError}
          </div>
        )}

        {!isLoading && !listError && documents.length === 0 && (
          <p className="dashboard-status-text">
            No documents uploaded for this application.
          </p>
        )}

        {!isLoading &&
          !listError &&
          documents.map((doc) => (
            <div className="document-row" key={doc.id}>
              <div>
                <p className="document-row-type">
                  {documentTypeLabel(doc.document_type)}
                  {doc.is_active && (
                    <span className="document-current-tag">Current</span>
                  )}
                </p>
                <p className="document-row-filename">
                  {doc.original_filename}
                  {doc.file_size !== undefined && doc.file_size !== null
                    ? ` · ${formatFileSize(doc.file_size)}`
                    : ""}
                  {doc.version_number
                    ? ` · Version ${doc.version_number}`
                    : ""}
                </p>
              </div>
              <span className="document-status-badge">
                {doc.is_active ? "CURRENT" : "HISTORICAL"}
              </span>
            </div>
          ))}
      </div>
    </div>
  );
}
