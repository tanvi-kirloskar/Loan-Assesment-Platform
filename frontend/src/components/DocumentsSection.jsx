import { useState, useEffect, useCallback } from "react";
import {
  listDocuments,
  viewDocument,
  uploadDocument,
  resubmitApplication,
  ApiError,
} from "../services/api";

const DOCUMENT_TYPE_OPTIONS = [
  { label: "Payslip", value: "PAYSLIP" },
  { label: "Bank Statement", value: "BANK_STATEMENT" },
  { label: "Tax Return", value: "TAX_RETURN" },
];

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

export default function DocumentsSection({
  applicationId,
  onSessionExpired,
  allowReplacement = false,
  onResubmitted,
}) {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [listError, setListError] = useState(null);
  const [viewingDocumentId, setViewingDocumentId] = useState(null);
  const [viewError, setViewError] = useState(null);
  const [replacementFiles, setReplacementFiles] = useState({});
  const [uploadingType, setUploadingType] = useState(null);
  const [resubmitting, setResubmitting] = useState(false);
  const [replacementMessage, setReplacementMessage] = useState(null);

  const loadDocuments = useCallback(async () => {
    setIsLoading(true);
    setListError(null);

    try {
      const result = await listDocuments(applicationId);
      // Historical versions stay available to the backend audit trail.
      // Applicants only see the currently submitted document for each type.
      setDocuments(result.filter((document) => document.is_active));
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

  async function handleReplacementUpload(documentType, file) {
    if (!file) return;
    setUploadingType(documentType);
    setReplacementMessage(null);
    try {
      await uploadDocument(applicationId, documentType, file);
      setReplacementFiles((current) => ({ ...current, [documentType]: null }));
      setReplacementMessage(`${documentTypeLabel(documentType)} uploaded successfully. You can resubmit once all requested documents are updated.`);
      await loadDocuments();
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setReplacementMessage(
        error instanceof ApiError
          ? error.message
          : "The replacement document could not be uploaded."
      );
    } finally {
      setUploadingType(null);
    }
  }

  async function handleResubmit() {
    setResubmitting(true);
    setReplacementMessage(null);
    try {
      await resubmitApplication(applicationId);
      setReplacementMessage("Application resubmitted successfully. Verification is running again.");
      if (onResubmitted) onResubmitted();
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setReplacementMessage(
        error instanceof ApiError
          ? error.message
          : "The application could not be resubmitted."
      );
    } finally {
      setResubmitting(false);
    }
  }

  async function handleViewDocument(document) {
    const previewWindow = window.open("", "_blank");

    if (!previewWindow) {
      setViewError("Please allow pop-ups to view your submitted document.");
      return;
    }

    setViewError(null);
    setViewingDocumentId(document.id);

    try {
      const blob = await viewDocument(applicationId, document.id);
      const blobUrl = URL.createObjectURL(blob);

      previewWindow.location.href = blobUrl;
      window.setTimeout(() => URL.revokeObjectURL(blobUrl), 60_000);
    } catch (error) {
      previewWindow.close();

      if (error instanceof ApiError && error.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }

      setViewError(
        error instanceof ApiError
          ? error.message
          : "The document could not be opened."
      );
    } finally {
      setViewingDocumentId(null);
    }
  }

  return (
    <div className="documents-section">
      <h3 className="detail-section-heading">Submitted Documents</h3>
      <p className="documents-intro">
        These are the documents you submitted with this application. You can
        view them at any time.
      </p>

      {viewError && (
        <div className="submit-error" role="alert">
          {viewError}
        </div>
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
            No submitted documents found for this application.
          </p>
        )}

        {!isLoading &&
          !listError &&
          documents.map((doc) => (
            <div className="document-row" key={doc.id}>
              <div className="document-row-main">
                <p className="document-row-type">
                  {documentTypeLabel(doc.document_type)}
                </p>
                <p className="document-row-filename">
                  {doc.original_filename}
                  {doc.file_size !== undefined && doc.file_size !== null
                    ? ` · ${formatFileSize(doc.file_size)}`
                    : ""}
                </p>
              </div>

              <button
                type="button"
                className="document-view-button"
                onClick={() => handleViewDocument(doc)}
                disabled={viewingDocumentId === doc.id}
              >
                {viewingDocumentId === doc.id ? "Opening…" : "View Document"}
              </button>
            </div>
          ))}
      </div>

      {allowReplacement && (
        <div className="document-replacement-panel">
          <h4>Update requested documents</h4>
          <p className="documents-intro">Replace the document requested by your advisor. Uploading a new version keeps the previous version in the audit history.</p>
          <div className="replacement-list">
            {documents.map((doc) => (
              <div className="replacement-row" key={doc.document_type}>
                <div>
                  <strong>{documentTypeLabel(doc.document_type)}</strong>
                  <span>{doc.original_filename}</span>
                </div>
                <label className="upload-choose-button">
                  {uploadingType === doc.document_type ? "Uploading…" : "Choose replacement"}
                  <input
                    type="file"
                    accept="application/pdf"
                    hidden
                    disabled={uploadingType !== null || resubmitting}
                    onChange={(event) => handleReplacementUpload(doc.document_type, event.target.files?.[0])}
                  />
                </label>
              </div>
            ))}
          </div>
          {replacementMessage && <p className="document-replacement-message" role="status">{replacementMessage}</p>}
          <button
            type="button"
            className="submit-button upload-submit-button"
            disabled={uploadingType !== null || resubmitting}
            onClick={handleResubmit}
          >
            {resubmitting ? "Resubmitting…" : "Resubmit Application"}
          </button>
        </div>
      )}
    </div>
  );
}
